import discord
from discord.ext import commands


class NewMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))

    @commands.Cog.listener()
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.bot.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')


async def setup(bot):
    await bot.add_cog(NewMember(bot))
