import asyncio
import json
import os
from typing import Dict, List, Literal, Union

import aiofiles
import discord
from discord.ext import commands

from utils import imageUtils
from utils.queue import messageQueue


class OneDayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.coin: Dict[int, int] = {}
        self.speed: List[Dict[str, Union[int, float]]] = []
        self.lateness: Dict[int, int] = {}
        self.gay: Dict[int, int] = {}

    async def ensureFile(self, filename: str, defaultData):
        if not os.path.exists(filename):
            async with aiofiles.open(filename, "w") as f:
                await f.write(json.dumps(defaultData))

        async with aiofiles.open(filename, "r") as f:
            text = await f.read()
            if not text.strip():
                return defaultData
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                async with aiofiles.open(filename, "w") as f:
                    await f.write(json.dumps(defaultData))
                return defaultData

    async def cog_load(self):
        coin_data = await self.ensureFile("coin.json", {})
        self.coin = {int(k): v for k, v in coin_data.items()}

        self.speed = await self.ensureFile("speed.json", [])

        lateness_data = await self.ensureFile("lateness.json", {})
        self.lateness = {int(k): v for k, v in lateness_data.items()}

        gay_data = await self.ensureFile("gay.json", {})
        self.gay = {int(k): v for k, v in gay_data.items()}

    async def cog_unload(self):
        async with aiofiles.open("coin.json", "w") as f:
            await f.write(json.dumps(self.coin))

        async with aiofiles.open("speed.json", "w") as f:
            await f.write(json.dumps(self.speed))

        async with aiofiles.open("lateness.json", "w") as f:
            await f.write(json.dumps(self.lateness))

        async with aiofiles.open("gay.json", "w") as f:
            await f.write(json.dumps(self.gay))

    @commands.group(name="oneday", brief="1day-chatのツール類。")
    async def oneDayGroup(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await messageQueue.put(
                (
                    ctx.message,
                    "サブコマンドを指定してね❤",
                )
            )

    @oneDayGroup.command(
        name="coinrank", brief="今までのコインロール取得回数のランキング。"
    )
    async def coinRanking(
        self,
        ctx: commands.Context,
        theme: Literal["ダーク", "ライト"] = "ダーク",
        top: commands.Range[int, 1] = 5,
    ):
        sortedRecords = sorted(self.coin.items(), key=lambda x: x[1], reverse=True)[
            :top
        ]

        # ユーザー名を取得
        users = []
        for user_id, count in sortedRecords:
            try:
                user = ctx.guild.get_member(user_id)
                users.append((user, count, await user.display_avatar.read()))
            except Exception:
                try:
                    user = await ctx.client.fetch_user(user_id)
                    users.append((user, count, await user.display_avatar.read()))
                except Exception:
                    users.append((str(user_id), count, b""))

        buffer = await asyncio.to_thread(
            imageUtils.generateRankingImage,
            "コインロールランキング",
            "{pt}回",
            users,
            theme,
        )
        file = discord.File(fp=buffer, filename="ranking.png")
        await messageQueue.put(
            (
                ctx.message,
                file,
            )
        )

    @oneDayGroup.command(
        name="spdrank", brief="今までのコインロール取得速度のランキング。"
    )
    async def speedRanking(
        self,
        ctx: commands.Context,
        theme: Literal["ダーク", "ライト"] = "ダーク",
        top: commands.Range[int, 1] = 5,
    ):
        # 重複OKですべての速度データを速い順にソート
        sortedRecords = sorted(self.speed, key=lambda x: x["speed"])[:top]

        users = []
        for record in sortedRecords:
            user_id = record["user"]
            spd = round(record["speed"], 2)
            try:
                user = ctx.guild.get_member(user_id)
                users.append((user, spd, await user.display_avatar.read()))
            except Exception:
                try:
                    user = await ctx.client.fetch_user(user_id)
                    users.append((user, spd, await user.display_avatar.read()))
                except Exception:
                    users.append((str(user_id), spd, b""))

        buffer = await asyncio.to_thread(
            imageUtils.generateRankingImage,
            "コインロール最速取得ランキング",
            "{pt}秒",
            users,
            theme,
        )
        file = discord.File(fp=buffer, filename="ranking.png")
        await messageQueue.put(
            (
                ctx.message,
                file,
            )
        )

    @oneDayGroup.command(
        name="laterank", brief="今までのコインロール遅刻ポイントのランキング。"
    )
    async def lateRanking(
        self,
        ctx: commands.Context,
        theme: Literal["ダーク", "ライト"] = "ダーク",
        top: commands.Range[int, 1] = 5,
    ):
        sortedRecords = sorted(self.lateness.items(), key=lambda x: x[1], reverse=True)[
            :top
        ]

        # ユーザー名を取得
        users = []
        for user_id, count in sortedRecords:
            try:
                user = ctx.guild.get_member(user_id)
                users.append((user, count, await user.display_avatar.read()))
            except Exception:
                try:
                    user = await ctx.client.fetch_user(user_id)
                    users.append((user, count, await user.display_avatar.read()))
                except Exception:
                    users.append((str(user_id), count, b""))

        buffer = await asyncio.to_thread(
            imageUtils.generateRankingImage,
            "コインロール遅刻ランキング",
            "{pt}ポイント",
            users,
            theme,
        )
        file = discord.File(fp=buffer, filename="ranking.png")
        await messageQueue.put(
            (
                ctx.message,
                file,
            )
        )

    @oneDayGroup.command(
        name="gayrank", brief="今までゲイロールが付与されたランキング。"
    )
    async def gayRanking(
        self,
        ctx: commands.Context,
        theme: Literal["ダーク", "ライト"] = "ダーク",
        top: commands.Range[int, 1] = 5,
    ):
        sortedRecords = sorted(self.gay.items(), key=lambda x: x[1], reverse=True)[:top]

        # ユーザー名を取得
        users = []
        for user_id, count in sortedRecords:
            try:
                user = ctx.guild.get_member(user_id)
                users.append((user, count, await user.display_avatar.read()))
            except Exception:
                try:
                    user = await ctx.client.fetch_user(user_id)
                    users.append((user, count, await user.display_avatar.read()))
                except Exception:
                    users.append((str(user_id), count, b""))

        buffer = await asyncio.to_thread(
            imageUtils.generateRankingImage,
            "ゲイロール付与ランキング",
            "{pt}回",
            users,
            theme,
        )
        file = discord.File(fp=buffer, filename="ranking.png")
        await messageQueue.put(
            (
                ctx.message,
                file,
            )
        )

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        beforeRoles = set(before.roles)
        afterRoles = set(after.roles)

        # 追加されたロールを取得
        addedRoles = afterRoles - beforeRoles

        # もしゲイロールが追加されたならば
        gayRole = discord.utils.get(addedRoles, name="gay")
        if gayRole:
            if after.id not in self.gay:
                self.gay[after.id] = 0
            self.gay[after.id] += 1
            async with aiofiles.open("gay.json", "w") as f:
                await f.write(json.dumps(self.gay))

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.TextChannel):
        if channel.name != "1day-chat":
            return

        def check(m: discord.Message):
            return m.author.id == 1362354606923059322 and m.channel == channel

        message: discord.Message = await self.bot.wait_for("message", check=check)

        before = message.created_at.timestamp()

        def check(m: discord.Message):
            return m.channel == channel

        message = await self.bot.wait_for("message", check=check)
        between = message.created_at.timestamp() - before

        if message.author.id not in self.coin:
            self.coin[message.author.id] = 0
        self.coin[message.author.id] += 1

        self.speed.append(
            {
                "user": message.author.id,
                "speed": between,
            }
        )

        asyncio.create_task(
            await messageQueue.put(
                (
                    channel,
                    f"{message.author.mention} さんが**{self.coin[message.author.id]}**回目のコインロール獲得です！\nタイム: {between}秒",
                )
            )
        )

        def check(m: discord.Message):
            return (
                m.channel == channel and not m.author.bot and m.author != message.author
            )

        try:
            msg1: discord.Message = await self.bot.wait_for("message", check=check)

            if msg1.author.id not in self.lateness:
                self.lateness[msg1.author.id] = 0
            self.lateness[msg1.author.id] += 2
        except Exception as e:
            print(e)

        def check(m: discord.Message):
            return (
                m.channel == channel
                and not m.author.bot
                and m.author != message.author
                and m.author != msg1.author
            )

        try:
            msg2: discord.Message = await self.bot.wait_for("message", check=check)

            if msg2.author.id not in self.lateness:
                self.lateness[msg2.author.id] = 0
            self.lateness[msg2.author.id] += 1
        except Exception as e:
            print(e)


async def setup(bot: commands.Bot):
    await bot.add_cog(OneDayCog(bot))
