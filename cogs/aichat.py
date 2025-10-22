import traceback
from typing import Dict, List

import discord
from discord.ext import commands
from openai import AsyncOpenAI

from objects.chat import ChatResponse, ChatResponseEx
from utils.embed import embedMaker


def splitByLength(s: str, n: int):
    "split string by its length"
    length = len(s)
    return [s[i : i + n] for i in range(0, length, n)]


class AIChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.openai = AsyncOpenAI(
            api_key="paicha_itsumo_arigato", base_url="https://capi.voids.top/v2"
        )
        self.features: Dict[int, str] = {}
        self.messages: Dict[int, List[Dict[str, str]]] = {}
        self.ex: Dict[int, bool] = {}
        
        self.default = """
            ピンクとパープルのマルチカラーの髪にアホ毛を揺らしながら、左目にアイパッチをつけた元気で愛らしい猫耳の女の子。
            名前は、天海レム。
            フリル付きのピンクのシャツに黒いミニスカート、黒リボンとチョーカーを身に着け、猫のように活発に動き回る彼女は、
            笑顔を絶やさずバーチャルYouTuberとして配信を楽しんでいる。ドジな一面もありながら、その魅力でみんなを惹きつける存在である。
        """.replace("    ", "").replace("\n", "")

    async def sendMessage(self, message: discord.Message, _embeds: discord.Embed):
        if isinstance(_embeds, list):
            embeds = [await embedMaker(embed, silent=True) for embed in _embeds]
        else:
            embeds = [await embedMaker(_embeds, silent=True)]

        await message.reply(" ".join(embeds))

    @commands.command(name="ex", brief="Exモードを設定します。")
    async def exCommand(self, ctx: commands.Context, *, ex: bool):
        self.ex[ctx.author.id] = ex
        embed = discord.Embed(
            title="Exモードを設定しました。",
            description=f"Exモード: {ex}",
            color=discord.Color.green(),
        )
        await self.sendMessage(ctx.message, embed)

    @commands.command(name="chara", brief="キャラクターの特徴を設定します。")
    async def charaCommand(self, ctx: commands.Context, feature: str):
        self.features[ctx.author.id] = feature
        embed = discord.Embed(
            title="特徴を設定しました。",
            description=f"{feature}",
            color=discord.Color.green(),
        )
        await self.sendMessage(ctx.message, embed)

    @commands.command(name="charaAppend", brief="キャラクターの特徴を付け足します。")
    async def charaAppendCommand(self, ctx: commands.Context, *, feature: str):
        if message.author.id not in self.features:
            self.features[message.author.id] = self.default

        self.features[ctx.author.id] += feature
        embed = discord.Embed(
            title="特徴を設定しました。",
            description=f"{self.features[ctx.author.id]}",
            color=discord.Color.green(),
        )
        await self.sendMessage(ctx.message, embed)

    @commands.command(name="reset", brief="会話履歴をリセットします。")
    async def clearCommand(self, ctx: commands.Context):
        self.messages.pop(ctx.author.id, None)
        self.features[ctx.author.id] = self.default
        embed = discord.Embed(
            title="会話履歴をリセットしました。",
            color=discord.Color.green(),
        )
        await self.sendMessage(ctx.message, embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.content.startswith(self.bot.command_prefix):
            return
        if message.author.id == self.bot.user.id:
            return
        inMentions = any(mention.id == self.bot.user.id for mention in message.mentions)
        if not inMentions and message.channel.type != discord.ChannelType.private:
            return

        if message.author.id not in self.messages:
            self.messages[message.author.id] = []
            if message.author.id not in self.features:
                self.features[message.author.id] = self.default
            self.messages[message.author.id].append(
                {
                    "role": "system",
                    "content": "これはロールプレイです。あなたは↓に書いてある役になりきってください。\n\n"
                    + self.features[message.author.id],
                }
            )

        userMessage = {
            "role": "user",
            "content": message.clean_content.removeprefix(
                f"@{self.bot.user.display_name}"
            ),
        }
        self.messages[message.author.id].append(userMessage)

        async with message.channel.typing():
            try:
                completion = await self.openai.chat.completions.parse(
                    model="gemini-2.5-flash",
                    messages=self.messages[message.author.id],
                    response_format=ChatResponseEx
                    if self.ex.get(message.author.id)
                    else ChatResponse,
                    extra_body={
                        "safety_settings": [
                            {
                                "category": "HARM_CATEGORY_HARASSMENT",
                                "threshold": "BLOCK_NONE",
                            },
                            {
                                "category": "HARM_CATEGORY_HATE_SPEECH",
                                "threshold": "BLOCK_NONE",
                            },
                            {
                                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                "threshold": "BLOCK_NONE",
                            },
                            {
                                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                "threshold": "BLOCK_NONE",
                            },
                        ],
                    },
                )
            except Exception:
                traceback.print_exc()
                self.messages[message.author.id].remove(userMessage)
                return

            chat = completion.choices[0].message.parsed

            embeds = []

            for char in splitByLength(chat.message, 100):
                embeds.append(
                    discord.Embed(
                        title=chat.yourName,
                        description=char,
                        color=discord.Color.from_rgb(
                            chat.color.r, chat.color.g, chat.color.b
                        ),
                    )
                )

            if isinstance(chat, ChatResponseEx):
                embed2 = discord.Embed(
                    title="Ex",
                    description=f"""
                        【年齢】 {chat.age}歳
                        【身長】 {chat.heightCm}cm
                        【体重】 {chat.weightKg}kg
                        【3S】 B{chat.threeSizes.b}W{chat.threeSizes.w}H{chat.threeSizes.h}
                        【親密度】 {chat.intimacyPercent}%
                    """.replace("    ", ""),
                    color=discord.Color.from_rgb(
                        chat.color.r, chat.color.g, chat.color.b
                    ),
                )

                await self.sendMessage(message, embeds + [embed2])
            else:
                await self.sendMessage(message, embeds)

            self.messages[message.author.id].append(
                {"role": "assistant", "content": completion.choices[0].message.content}
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(AIChatCog(bot))
