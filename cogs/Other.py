import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import config


class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Reserved for automated usage
    """
    @commands.command(brief="DM Welcome to the tagged member")
    async def dm(self, ctx, user: nextcord.Member, *, message=None):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            message = "Welcome to the server!"
            embed = nextcord.Embed(title=message)
            await user.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_roles=True)
    async def addRole(self, ctx, user: nextcord.Member, *, role: nextcord.Role):
        if role in user.roles:
            await ctx.send(f"{user.mention} already has the role, {role}")
        else:
            await user.add_roles(role)
            await ctx.send(f"Added {role} to {user.mention}")
    
    @commands.command(brief="Custom embedded message")
    async def customembed(self, ctx, Title=None, TitleUrl="https://title.link", Description=None,
                          ThumbnailUrl="https://thumbnail.link",
                          FieldTitle=None, FieldDescription=None, Footer=None):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            embed = nextcord.Embed(title=Title, url=TitleUrl, description=Description, color=0x4dff4d)
            # embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ThumbnailUrl)
            embed.add_field(name=FieldTitle, value=FieldDescription, inline=True)
            embed.set_footer(text=Footer)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        channel = reaction.message.channel
        print(f"{user.name} added {reaction.emoji}")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        channel = reaction.message.channel
        print(f"{user.name} removed {reaction.emoji}")

    """


def setup(client):
    client.add_cog(Other(client))
