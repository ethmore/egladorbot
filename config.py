import nextcord
from nextcord.ext import commands
import pymongo
import keys
import os

# ---- Database ----
mongo_client = pymongo.MongoClient(f"mongodb+srv://{keys.db_name}:{keys.db_password}"
                                   f"@cluster0.za3ns.mongodb.net/eglador_bot_db?retryWrites=true&w=majority")
bot_db = mongo_client["eglador_bot_db"]
db_config = bot_db["config"]
db_forbidden = bot_db["forbidden_coll"]

# ---- Globals ----
commandPrefix = str(None)
channelSelectivity = bool(None)
selectedChannel = str(None)
# intents = nextcord.Intents.default()
# intents.members = True
# client = commands.Bot(command_prefix=commandPrefix, intents=intents)

# ---- NOT Configurable Variables ----
guildID = [643857272216354866, 340277764907204608, 690613069826752573]  # IDs of guilds that allowed slash commands
allowMessages = False
initialExtensions = []

for x in db_config.find({"_id": 1}):
    print(x)
    commandPrefix = (x["prefix"])
    channelSelectivity = (x["channelSelectivity"])
    selectedChannel = (x["selectedChannel"])
    intents = nextcord.Intents.default()
    intents.members = True
    client = commands.Bot(command_prefix=commandPrefix, intents=intents)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        initialExtensions.append("cogs." + filename[:-3])


def load_extensions():
    for extension in initialExtensions:
        client.load_extension(extension)


def reload_extensions():
    for extension in initialExtensions:
        client.reload_extension(extension)


async def allowMsg(message):
    global allowMessages

    allowMessages = True
    channel = message.channel

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


async def update_bot_configs():
    global commandPrefix
    global channelSelectivity
    global selectedChannel
    global client
    global intents

    for y in db_config.find({"_id": 1}):
        print(y)
        commandPrefix = (y["prefix"])
        channelSelectivity = (y["channelSelectivity"])
        selectedChannel = (y["selectedChannel"])
        intents = nextcord.Intents.default()
        # client = commands.Bot(command_prefix=commandPrefix, intents=intents)
        reload_extensions()
    return
