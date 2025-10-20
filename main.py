import asyncio
import os

import dotenv
from discord.ext import commands

from utils.queue import queueLoop

dotenv.load_dotenv()

queueTask: asyncio.Task = None


class Bot(commands.Bot):
    async def close(self):
        queueTask.cancel()
        return await super().close()


bot = commands.Bot("rin!", help_command=None)


@bot.event
async def setup_hook():
    global queueTask

    queueTask = asyncio.create_task(queueLoop())

    await bot.load_extension("cogs.aichat")
    await bot.load_extension("cogs.oneday")
    await bot.load_extension("cogs.help")


bot.run(os.getenv("discord"))
