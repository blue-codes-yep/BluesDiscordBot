import discord
from discord.ext import commands
from discord.utils import get
import aiohttp
from valo_api import get_mmr_details_by_name_v1
from valo_api.exceptions.valo_api_exception import ValoAPIException


class NewMember(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self._last_member = None
        # ID of the message that can be reacted to to add/remove a role.
        self.role_message_id = 996982515904544768
        self.emoji_to_role = {
            # Iron
            discord.PartialEmoji(name='Iron_Valorant', id=996983352252977203): 996985470489727067,
            # Bronze
            discord.PartialEmoji(name='Bronze_Valorant', id=996983349547630672): 996987470711365633,
            # Silver
            discord.PartialEmoji(name='Silver_Valorant', id=996983350562656266): 996987607256928257,
            # Gold
            discord.PartialEmoji(name='Gold_Valorant', id=996983351460245514): 996987717290295366,
            # Plat
            discord.PartialEmoji(name='Platinum_Valorant', id=996983348599717958): 996988203112337428,
            # Diamond
            discord.PartialEmoji(name='Diamond_Valorant', id=996983353091821668): 996988286604161116,
            # Ascendant
            discord.PartialEmoji(name='Ascendant_Valorant', id=996983603579867257): 996988431181828116,
            # Immortal
            discord.PartialEmoji(name='Immortal_Valorant', id=996983353985224784): 996988637084405801,
            # Radiant
            discord.PartialEmoji(name='Radiant_Valorant', id=996983355960729610): 996988747931463690,
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
            print("Error on emoji_to_role")
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

    @commands.command(aliases=['valrank', 'checkrank', 'valorant'])
    async def valorant_rank(self, ctx, *, arg):
        async with ctx.typing():
            if len == 0:
                return await ctx.send(f'Error: Please enter a username.')
        name, _, tag = arg.partition("#")
        region, name = name[:2], name[2:]
        try:
            data = get_mmr_details_by_name_v1(region, name, tag)
            return await ctx.send(f'Rank: {data.currenttierpatched} - RR: {data.ranking_in_tier}')
        except ValoAPIException as e:
            print(e)

    @commands.command(aliases=['help', 'h'])
    async def help_section(self, ctx):
        embed = discord.Embed(
            title="Help", description=f'Commands Prefix:`{self.bot.command_prefix}`', color=0xb2558d)

        embed.add_field(name=f'`{self.bot.command_prefix}upload_emoji emojiname` (Can also just say `!emoji`)',
                        value="Sets attached image as a custom server emoji with the given name.",
                        inline=False)

        embed.add_field(name=f'`{self.bot.command_prefix}checkrank naReallyBlue#NA1` (aka `!valrank`, `!checkrank`, `!valorant`)',
                        value="Check your current Valorant rank, and RR rating. Region must be lowercase. `Region`,`Username`,`Tag`",
                        inline=False)

        embed.set_footer(text="Contact ! Blue#0921 with issues.")
        return await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(NewMember(bot))
