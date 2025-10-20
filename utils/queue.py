import asyncio

import discord

messageQueue = asyncio.Queue()


async def queueLoop():
    while True:
        message, content = await messageQueue.get()

        if isinstance(message, discord.Message):
            if isinstance(content, discord.File):
                await message.reply(file=content)
            else:
                await message.reply(content)
        elif isinstance(message, discord.abc.Messageable):
            if isinstance(content, discord.File):
                await message.send(file=content)
            else:
                await message.send(content)

        await asyncio.sleep(2)
