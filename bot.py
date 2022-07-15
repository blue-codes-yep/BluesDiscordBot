import discord
from discord.ext import commands
import os
from dotenv import load_dotenv


class MyBot(commands.Bot):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def setup_hook(self):
        await self.load_extension('events')


load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
Bot = MyBot(intents=intents, command_prefix='!', help_command=None)
Bot.run(os.getenv('TOKEN'))
