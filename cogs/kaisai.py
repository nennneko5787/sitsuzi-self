import base64
import traceback
from typing import Dict, List

import discord
from discord.ext import commands
from openai import AsyncOpenAI

from utils.embed import embedMaker


def splitByLength(s: str, n: int):
    "split string by its length"
    length = len(s)
    return [s[i : i + n] for i in range(0, length, n)]


class KaisaiChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.openai = AsyncOpenAI(
            api_key="paicha_itsumo_arigato", base_url="https://capi.voids.top/v2"
        )
        self.messages: Dict[int, List[Dict[str, str]]] = {}
        self.default = """
            ピンクとパープルのマルチカラーの髪を無造作に垂らし、風になびくアホ毛が印象的な少女。
            左目には黒いアイパッチをつけ、どこか挑発的な笑みを浮かべる。猫耳がぴくりと動くたび、周囲の視線をさらっていく。

            フリル付きのピンクシャツに、黒のミニスカート。
            その上からショートジャケットを羽織り、腰にはチェーンアクセを揺らす。
            黒いチョーカーとリボンをつけた姿は、可愛らしさの中に危うい鋭さを感じさせる。

            誰にでも媚びない。だけど、気まぐれに心を許した相手には、猫のように懐く。
            口調は少し乱暴で、ついツンとした態度をとってしまうこともあるが、根は情に厚く、困っている人を放っておけない。

            街の夜風のように自由奔放で、退屈を嫌う彼女は、
            今日もどこかでピンクの髪を揺らしながら、自分の思うままに生きている。

            ちなみに貧乳。
        """.replace("    ", "").replace("\n", "")

    async def sendMessage(self, message: discord.Message, _embeds: discord.Embed):
        if isinstance(_embeds, list):
            embeds = [await embedMaker(embed, silent=True) for embed in _embeds]
        else:
            embeds = [await embedMaker(_embeds, silent=True)]

        await message.reply(" ".join(embeds))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.content.startswith(self.bot.command_prefix):
            return
        if message.author.id != 1427189323983491164:
            return
        if message.guild.id != 1403269573704290335:
            return

        if message.author.id not in self.messages:
            self.messages[message.author.id] = []
            self.messages[message.author.id].append(
                {
                    "role": "system",
                    "content": "私の名前はかいさいです。あなたは、かいさいとレスバしてください。\nあなたの人格は以下のとおりです。\n\n"
                    + self.default,
                }
            )

        content = [
            {
                "type": "input_text",
                "text": message.clean_content.removeprefix(
                    f"@{self.bot.user.display_name}"
                ),
            }
        ]

        for attachment in message.attachments:
            if attachment.content_type:
                content.append(
                    {
                        "type": "input_image",
                        "image_url": f"data:{attachment.content_type};base64,{base64.b64encode(await attachment.read()).decode()}",
                    },
                )

        userMessage = {
            "role": "user",
            "content": content,
        }
        self.messages[message.author.id].append(userMessage)

        async with message.channel.typing():
            try:
                completion = await self.openai.chat.completions.create(
                    model="gemini-2.5-pro",
                    messages=self.messages[message.author.id],
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

            chat = completion.choices[0].message.content

            embeds = []

            for char in splitByLength(chat, 100):
                embeds.append(
                    discord.Embed(
                        description=char,
                    )
                )
            await self.sendMessage(message, embeds)

            self.messages[message.author.id].append(
                {"role": "assistant", "content": completion.choices[0].message.content}
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(KaisaiChatCog(bot))
