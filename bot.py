import discord
from discord.ext import commands
import events
import asyncio


class MyBot(commands.Bot):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def setup_hook(self):
        await self.load_extension('events')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
Bot = MyBot(intents=intents, command_prefix='!')
Bot.run('token')
