import asyncio
import os

import dotenv
from discord.ext import commands


dotenv.load_dotenv()

bot = commands.Bot("rem!", help_command=None)


@bot.event
async def setup_hook():
    await bot.load_extension("cogs.aichat")
    await bot.load_extension("cogs.oneday")
    await bot.load_extension("cogs.help")


bot.run(os.getenv("discord"))
