import nextcord
from nextcord.ext import commands

# from nextcord.ext.commands import has_permissions
from nextcord.ext.commands import MissingPermissions

commandPrefix = '.'


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = self.client.get_channel(message.channel.id)
        if (channel.name != 'bot-commands' and message.content.startswith(commandPrefix)) or \
                channel.name == 'bot-commands' and not message.content.startswith(commandPrefix):
            await message.delete()

    # Kick any member with or without a reason
    @commands.command(brief="Kick any member w/wout a reason")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: nextcord.Member, *, reason=None):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            try:
                await member.kick(reason=reason)
                await ctx.send(f'User **{member}** has been kicked by **{ctx.author}**! Reason: **{reason}**')
            except nextcord.Forbidden:
                await ctx.send(f"I don't have permission to kick **{member}**")

    # Kick error catch
    @kick.error
    async def kickError(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have permission to kick people!")

    # Ban any member with or without a reason
    @commands.command(brief="Ban any member w/wout a reason")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: nextcord.Member, *, reason=None):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            try:
                await member.ban(reason=reason)
                await ctx.send(f'User **{member}** has been banned by **{ctx.author}**! Reason: **{reason}**')
            except nextcord.Forbidden:
                await ctx.send(f"I don't have permission to ban **{member}**")

    # Ban error catch
    @ban.error
    async def banError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to ban people!")

    # DM Welcome message
    @commands.command(brief="DM Welcome to the tagged member")
    async def dm(self, ctx, user: nextcord.Member, *, message=None):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            message = "Welcome to the server!"
            embed = nextcord.Embed(title=message)
            await user.send(embed=embed)

    @dm.error
    async def dmError(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'```Wrong syntax. Proper usage: {commandPrefix}dm @MEMBER```')

    # WIP Message delete command
    @commands.command(brief="[WIP] Deletes message", pass_context=True)
    async def delete(self, ctx):
        # author = ctx.message.author
        await ctx.message.delete()
        await ctx.send("Deleted [WIP]")

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_roles=True)
    async def addRole(self, ctx, user: nextcord.Member, *, role: nextcord.Role):
        if role in user.roles:
            await ctx.send(f"{user.mention} already has the role, {role}")
        else:
            await user.add_roles(role)
            await ctx.send(f"Added {role} to {user.mention}")

    @addRole.error
    async def roleError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command")

    # Test response
    @commands.command()
    async def test(self, ctx):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            thumbsUp = '\U0001F44D'
            await ctx.message.add_reaction(thumbsUp)


def setup(client):
    client.add_cog(Moderation(client))
