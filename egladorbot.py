from __future__ import unicode_literals
import nextcord
# from nextcord import Interaction
from nextcord.ext import commands
from keys import *  # Bot & API Keys
import config

#
# intents = nextcord.Intents.default()
# intents.members = True
# client = commands.Bot(command_prefix=config.commandPrefix, intents=intents)


# Bot Startup
@config.client.event
async def on_ready():
    await config.client.change_presence(activity=nextcord.Streaming(name="Slash commands", url=""))
    print('Logged in as {0.user}'.format(config.client))


if __name__ == '__main__':
    config.load_extensions()
    from cogs import *


# Command error catch
@config.client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("```You don't have permission to run this command```")
    elif isinstance(error, commands.MissingRequiredArgument):
        # await ctx.send('```Missing Argument.```')
        pass
    elif isinstance(error, commands.CommandNotFound):
        await ctx.message.delete()
        # await ctx.send(f"`There's no such command. Type {config.commandPrefix}help for all commands`")


config.client.run(TOKEN)
