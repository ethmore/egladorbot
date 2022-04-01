import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import MissingPermissions
import config


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = self.client.get_channel(message.channel.id)

        if config.channelSelectivity is True:   # Channel selectivity check
            if channel.name == config.selectedChannel and not message.content.startswith(config.commandPrefix) and message.author != self.client.user:
                await message.delete()  # Channel TRUE, prefix FALSE, message NOT belongs to the bot
                config.allowMessages = False
            elif channel.name != config.selectedChannel and message.content.startswith(config.commandPrefix) and message.author != self.client.user:
                await message.delete()  # Channel FALSE, prefix TRUE, message NOT belongs to the bot
                config.allowMessages = False
        else:
            config.allowMessages = False

    # Test response
    @commands.command()
    async def test(self, ctx):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            await ctx.message.add_reaction('\U0001F44D')  # Thumbs up emoji

    @commands.command(brief="Re Define command prefix")
    async def prefix(self, ctx, new_prefix):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            old_db_prefix = {"prefix": f"{ctx.prefix}"}
            new_db_prefix = {"$set": {"prefix": f"{new_prefix}"}}
            config.db_collection.update_one(old_db_prefix, new_db_prefix)
            # config.reload_extensions()
            await config.update_bot_configs()
            # await config.client.process_commands(ctx.message)
            await ctx.send(f"```New prefix for bot is '{new_prefix}'``")

    @commands.command(brief="Kick any member w/wout a reason")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: nextcord.Member, *, reason=None):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            try:
                await member.kick(reason=reason)
                await ctx.send(f'User **{member}** has been kicked by **{ctx.author}**! Reason: **{reason}**')
            except nextcord.Forbidden:
                await ctx.send(f"I don't have permission to kick **{member}**")

    @kick.error
    async def kickError(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have permission to kick people!")

    @commands.command(brief="Ban any member w/wout a reason")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: nextcord.Member, *, reason=None):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            try:
                await member.ban(reason=reason)
                await ctx.send(f'User **{member}** has been banned by **{ctx.author}**! Reason: **{reason}**')
            except nextcord.Forbidden:
                await ctx.send(f"I don't have permission to ban **{member}**")

    @ban.error
    async def banError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to ban people!")

    @commands.command(brief="DM Welcome to the tagged member")
    async def dm(self, ctx, user: nextcord.Member, *, message=None):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            message = "Welcome to the server!"
            embed = nextcord.Embed(title=message)
            await user.send(embed=embed)

    @dm.error
    async def dmError(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'```Proper usage: {config.commandPrefix}dm @MEMBER```')

    # WIP - WIP - WIP - WIP - WIP - WIP
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


def setup(client):
    client.add_cog(Moderation(client))
