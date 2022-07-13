import discord
from discord.ext import commands
from discord.utils import get
import aiohttp


class NewMember(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self._last_member = None
        # ID of the message that can be reacted to to add/remove a role.
        self.role_message_id = 996290080115269692
        self.emoji_to_role = {
            # ID of the role associated with unicode emoji '🔴'.
            discord.PartialEmoji(name='🔴'): 996308087755526154,
            # ID of the role associated with unicode emoji '🟡'.
            discord.PartialEmoji(name='🟡',): 996308265606594601,
            # ID of the role associated with a partial emoji's ID.
            discord.PartialEmoji(name='green', id=0): 996308551641350195,
        }

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.role_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        try:
            # Adding the role
            await payload.member.add_roles(role)
        except discord.HTTPException:
            print("Error adding role")
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):

        if payload.message_id != self.role_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            # If the emoji isn't the one we care about then exit as well.
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        # The payload for `on_raw_reaction_remove` does not provide `.member`
        # so we must get the member ourselves from the payload's `.user_id`.
        member = guild.get_member(payload.user_id)
        if member is None:
            # Making sure member exist
            return

        try:
            # Remove role.
            await member.remove_roles(role)
        except discord.HTTPException:
            print("Error removing role")
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))

    @commands.command(aliases=['emoji'])
    async def upload_emoji(self, ctx, *args):
        async with ctx.typing():
            if len == 0:
                return await ctx.send(f'Error: Give the emoji a name.')
        name = args[0]
        if len(name) < 2 or len(name) > 32:
            return await ctx.send(f"Error: Name of the emoji has to be between 2, and 32 characters.")
        if name in str(ctx.guild.emojis):
            return await ctx.send("Error: Emoji name is already used.")
        try:
            emoji_image = ctx.message.attachments[0].url
        except IndexError:
            return await ctx.send(f'Error: Please attach the image to your message, by uploading it to the message.')

        extensions = [".png", ".jpg", ".jpeg"]
        if not any(ext in emoji_image.lower() for ext in extensions):
            return await ctx.send(f'Please make sure that the image format is a "png", "jpg", or "jpeg"')

        if len(ctx.guild.emojis) >= ctx.guild.emoji_limit:
            return await ctx.send(f'All emoji slots ({ctx.guild.emoji_limit}) have been filled.')

        async with aiohttp.ClientSession() as session:
            async with session.get(emoji_image, timeout=20) as response:
                if response.ok:
                    image_bytes = await response.content.read()
                    try:
                        emoji = await ctx.guild.create_custom_emoji(name=name, image=image_bytes)
                    except aiohttp.ServerTimeoutError:
                        return await ctx.send(f'Server timed out, Try again.')
                    except Exception as e:
                        if "String value did not match validation regex" in str(e):
                            return await ctx.send(f'No special characters allowed')
                        return await ctx.send(e)
                    await ctx.send(f'New emoji: <:{emoji.name}:{emoji.id}> (`<:{emoji.name}:{emoji.id}`)')
                else:
                    await ctx.send(f'Something went wrong, please contact ! Blue#0921')
                    print(response.status)

    @commands.Cog.listener()
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.bot.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')


async def setup(bot):
    await bot.add_cog(NewMember(bot))
