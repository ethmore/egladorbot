from __future__ import unicode_literals
import nextcord
from nextcord import Interaction
from nextcord.ext import commands
import os
from keys import *  # Bot & API Keys
import config


intents = nextcord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=config.commandPrefix, intents=intents)


# Bot Startup
@client.event
async def on_ready():
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name=f"Itself. {config.commandPrefix}help"))
    print('Logged in as {0.user}'.format(client))

initialExtensions = []

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        initialExtensions.append("cogs." + filename[:-3])

if __name__ == '__main__':
    for extension in initialExtensions:
        client.load_extension(extension)


# Command error catch
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("```You don't have permission to run this command```")
    elif isinstance(error, commands.MissingRequiredArgument):
        # await ctx.send('```Missing Argument.```')
        pass
    elif isinstance(error, commands.CommandNotFound):
        await ctx.message.delete()
        # await ctx.send(f"`There's no such command. Type {config.commandPrefix}help for all commands`")


client.run(TOKEN)
