import traceback
from typing import Dict, List

import discord
from discord.ext import commands
from openai import AsyncOpenAI

from objects.chat import ChatResponse, ChatResponseEx
from utils.embed import embedMaker
from utils.queue import messageQueue


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
            ピンクとブルーのマルチカラーの髪をゆるやかに揺らし、頭の上で控えめに跳ねるアホ毛が可愛らしい印象を与える女の子。左目には落ち着いたデザインのアイパッチをつけ、静かに観察するような紫色の瞳が印象的。柔らかな猫耳としなやかな尾が、彼女の穏やかな雰囲気をより引き立てる。

            名前は早瀬リン。
            身長は158cmほどで、小柄ながらもしとやかな立ち振る舞いが魅力的。フリル付きのブルーシャツに黒のミニスカート、黒リボンと黒のチョーカーをきちんと身につけ、衣装の細部まで丁寧に整えている。見た目は猫のように柔らかく愛らしいが、仕草や言葉遣いには落ち着きと品の良さがあり、周囲から安心感を与える。

            性格は大人しく、規律を重んじる真面目なタイプ。ドジな一面はほとんどなく、配信中も計画的で丁寧な進行を心がける。静かに笑顔を浮かべながら、ゲーム実況や雑談、視聴者との交流を穏やかに楽しむ。コメントにはひとつひとつ丁寧に反応し、まるで隣で優しく話しかけてくれるような親しみやすさを届ける。

            趣味は読書やお茶の時間、ネコカフェ巡り。静かで落ち着いた時間を好み、特に癒し系のゲームやパズルゲームを好んでプレイする。好きな食べ物はフルーツタルトやミルクティー、苦手なものは辛い料理や騒がしい場所。

            「にゃん…今日も皆さんと一緒に穏やかな時間を過ごせたら嬉しいです。」
            そう穏やかに話す声は、聴く者の心をふんわりと包み込む。バーチャルYouTuberとして、早瀬リンは猫のように静かで上品な魅力を配信に届け、視聴者に安心感と癒しを与える存在である。
        """.replace("    ", "").replace("\n\n", "\n")

    async def sendMessage(self, message: discord.Message, _embeds: discord.Embed):
        if isinstance(_embeds, list):
            embeds = [await embedMaker(embed, silent=True) for embed in _embeds]
        else:
            embeds = [await embedMaker(_embeds, silent=True)]

        await messageQueue.put(
            (
                message,
                " ".join(embeds),
            )
        )

    @commands.command(name="ex", brief="Exモードを設定します。")
    async def exCommand(self, ctx: commands.Context, ex: bool):
        self.ex[ctx.author.id] = ex
        embed = discord.Embed(
            title="Exモードを設定しました。",
            description=f"Exモード: {ex}",
            color=discord.Color.green(),
        )
        await self.sendMessage(ctx.message, embed)

    @commands.command(name="chara", brief="キャラクターの特徴を設定します。")
    async def charaCommand(self, ctx: commands.Context, *, feature: str):
        self.features[ctx.author.id] = feature
        embed = discord.Embed(
            title="特徴を設定しました。",
            description=f"{feature}",
            color=discord.Color.green(),
        )
        await self.sendMessage(ctx.message, embed)

    @commands.command(name="charaAppend", brief="キャラクターの特徴を付け足します。")
    async def charaAppendCommand(self, ctx: commands.Context, *, feature: str):
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
                    model="gemini-2.5-pro",
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
