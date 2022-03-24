import nextcord
from nextcord.ext import commands
from nextcord import Interaction

commandPrefix = '.'
testServerId = 643857272216354866


class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Basic embed message. Includes: Author and avatar, Linked title, Description
    @commands.command(brief="Basic embedded message test")
    async def basicembed(self, ctx):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            embed = nextcord.Embed(title="Başlık ve link", url="https://google.com", description="Açıklama", color=0x4dff4d)
            embed.set_author(name=ctx.author.display_name, url="https://fredboat.com/dashboard", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(brief="Advanced embedded message test")
    async def embedtest(self, ctx):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            embed = nextcord.Embed(title="Başlık ve link", url="https://eglador.com", description="Açıklama", color=0x4dff4d)
            # embed.set_author(name=ctx.author.display_name, url="https://fredboat.com/dashboard", icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url="https://images.pexels.com/photos/2832432/pexels-photo-2832432.png?auto=compress&cs=tinysrgb&dpr=1&w=500")
            embed.add_field(name="Alan 1", value="Minik açıklama", inline=True)
            embed.add_field(name="Alan 2", value="Minik açıklama 2", inline=True)
            embed.set_footer(text="Dipnot: aasddads")
            await ctx.send(embed=embed)

    @commands.command(brief="Custom embedded message")
    async def customembed(self, ctx, Title=None, TitleUrl="https://title.link", Description=None,
                          ThumbnailUrl="https://thumbnail.link",
                          FieldTitle=None, FieldDescription=None, Footer=None):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
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

    @nextcord.slash_command(name="oest", description="Slash online test", guild_ids=[])
    async def scog(self, interaction: Interaction):
        await interaction.response.send_message("pong")


def setup(client):
    client.add_cog(Other(client))
