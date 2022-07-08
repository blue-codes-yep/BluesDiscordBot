import discord
from discord.ext import commands
import events
import asyncio


class MyClient(commands.Bot):
    async def on_ready(self):
        print('Logged on as', self.user)


async def main():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    Bot = MyClient(intents=intents, command_prefix='!')

    async with Bot:
        await Bot.load_extension('events')
        await Bot.start(
            'NzYwMzA0NDMxNDA4NjExMzk4.G5PSjL.gb2AbDR6XqCI0eRoDkDdbyhmG9l-8HuBVxmmwM')

asyncio.run(main())
