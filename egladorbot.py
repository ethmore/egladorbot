from __future__ import unicode_literals
# from aiohttp import request
import nextcord
from nextcord import Interaction
from nextcord.ext import commands
import os
from keys import *  # Bot & API Keys

intents = nextcord.Intents.default()
intents.members = True
commandPrefix = '.'
client = commands.Bot(command_prefix=commandPrefix, intents=intents)


# Bot Startup
@client.event
async def on_ready():
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name=f"Itself. {commandPrefix}help"))
    print('Logged in as {0.user}'.format(client))

initialExtensions = []

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        initialExtensions.append("cogs." + filename[:-3])

if __name__ == '__main__':
    for extension in initialExtensions:
        client.load_extension(extension)

""" 
#Command error catch
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to run this command")
    elif isinstance(error, commands.MissingRequiredArgument):
        #await ctx.send('```Wrong syntax.```')
        pass
    else:
        await ctx.send(f"`There's no such command. Type {commandPrefix}helpall for all commands`")
 """
client.run(TOKEN)

# auto kick/ban
# Üye karşılama geliştirilecek
# Tepki/Emoji response
# Levelling

# Auto moderation
#       forbidden words

# Timer / Scheduler

# Channel / Member counters

# Follower counter
#       Instagram
#       Reddit
#       YouTube
#       Twitter

# Twitch integration - follower, stream

# Economy
#       Coin flip
#       Guess


# DONE - queue
# DONE - skip
# DONE - yt search
# DONE - playlist play
# DONE - auto delete forbidden channel messages

# Error catch

# Main error catch fonksiyonu geliştirilecek
# .stop command while not in a voice channel
