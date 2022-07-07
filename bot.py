import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = f'Welcome {member.mention} to the best {guild.name}!'
            await guild.system_channel.send(to_send)


intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run('NzYwMzA0NDMxNDA4NjExMzk4.G9HP_b.AAguTjsC-EBvBDozA1v7BAEnGcfEGPGlMWjEA4')
