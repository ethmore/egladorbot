import nextcord
from nextcord.ext import commands

# ---- Configurable Variables ----
commandPrefix = '.'  # Prefix for commands
channelSelectivity = True  # Ables/Disables operation on specific channel
selectedChannel = 'bot-commands'  # Specific channel's name

# ---- NOT Configurable Variables ----
guildID = [643857272216354866, 340277764907204608]  # IDs of guilds that allowed slash commands
allowMessages = False

intents = nextcord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=commandPrefix, intents=intents)


async def allowMsg(message):
    global allowMessages

    allowMessages = True
    channel = message.channel

    #  allowMessages false'a düştüğünde tekrar komuta cevap vermesi için önce TRUE olması gerekiyor

    if channelSelectivity is True:  # Channel selectivity check
        if channel.name == selectedChannel:
            if message.content.startswith(commandPrefix):
                allowMessages = True  # Channel and prefix is correct
            elif not message.content.startswith(commandPrefix):
                if message.author == client.user:
                    allowMessages = True  # Channel is correct but prefix WRONG and message belongs to the bot

    elif channelSelectivity is False:
        allowMessages = True
    else:
        allowMessages = False
