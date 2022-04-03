import nextcord
from nextcord.ext import commands
# from nextcord.ext.commands import MissingPermissions
import config
from nextcord import Interaction


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = self.client.get_channel(message.channel.id)

        if config.channelSelectivity is True:  # Channel selectivity check
            if channel.name == config.selectedChannel and not message.content.startswith(config.commandPrefix) and message.author != self.client.user:
                await message.delete()  # Channel TRUE, prefix FALSE, message NOT belongs to the bot
                config.allowMessages = False
            elif channel.name != config.selectedChannel and message.content.startswith(config.commandPrefix) and message.author != self.client.user:
                await message.delete()  # Channel FALSE, prefix TRUE, message NOT belongs to the bot
                config.allowMessages = False
        else:
            config.allowMessages = False

        # Forbidden word detection
        guildID = message.guild.id
        split_message = message.content.split(" ")
        db_forbidden_words = config.db_forbidden.count_documents({"server_id": guildID, "forbidden_word": {"$in": split_message}})

        if message.author != self.client.user:
            if db_forbidden_words > 0:
                await channel.send("That's forbidden!")
        else:
            pass  # That's me!

    @nextcord.slash_command(name="test", description="Up Test", guild_ids=config.guildID)
    async def test(self, interaction: Interaction):
        await interaction.send("Online")

    # WIP - WIP - WIP - WIP - WIP - WIP
    @nextcord.slash_command(name="delete", description="[WIP] Deletes message", guild_ids=config.guildID)
    async def delete(self, interaction: Interaction):
        # author = ctx.message.author
        await interaction.message.delete()
        await interaction.send("Deleted [WIP]")

    @nextcord.slash_command(name="forbidden", description="Adds a word to the forbidden words list", guild_ids=config.guildID)
    async def forbidden(self, interaction: Interaction, word):
        guildID = interaction.guild_id
        db_guild_word = config.db_forbidden.find_one({"server_id": guildID, "forbidden_word": word})

        if not db_guild_word:
            config.db_forbidden.insert_one({"server_id": guildID, "forbidden_word": word})
            await interaction.send("Word is added to the forbidden word list")
        else:
            await interaction.send("Word is already in list")
        # elif not data:
        #     guild_forbidden_dict = {"_id": guildID, "forbidden_words": [f"{word}"]}
        #     config.db_forbidden.insert_one(guild_forbidden_dict)

    @nextcord.slash_command(name="forbidden_delete", description="Removes a word from the forbidden words list", guild_ids=config.guildID)
    async def forbidden_delete(self, interaction: Interaction, word):
        guildID = interaction.guild_id
        db_guild_word = config.db_forbidden.find_one_and_delete({"server_id": guildID, "forbidden_word": word})

        if db_guild_word:
            await interaction.send("Word is removed from list")
        else:
            await interaction.send("Word is not in the forbidden list")

    @nextcord.slash_command(name="forbidden_listall", description="Lists all forbidden words", guild_ids=config.guildID)
    async def forbidden_listall(self, interaction: Interaction):
        guildID = interaction.guild_id
        forbidden_list_message = str("")
        db_guild_words = config.db_forbidden.find({"server_id": guildID}, {"_id": 0, "server_id": 0})

        for x in db_guild_words:
            forbidden_list_message += f"``{x['forbidden_word']}``, "
        forbidden_list_message = forbidden_list_message[:-2]

        if forbidden_list_message:
            embeds = nextcord.Embed(title=forbidden_list_message, color=0x4dff4d)
            await interaction.send(embed=embeds)
        else:
            await interaction.send("There is no forbidden words")

    @nextcord.slash_command(name="forbidden_update", description="Updates an existing word", guild_ids=config.guildID)
    async def forbidden_update(self, interaction: Interaction, old_word, new_word):
        guildID = interaction.guild_id
        db_guild_word = config.db_forbidden.find_one_and_update({"server_id": guildID, "forbidden_word": old_word},
                                                                {"$set": {"forbidden_word": new_word}})

        if db_guild_word:
            await interaction.send("Word is updated")
        else:
            await interaction.send(f"There is no such word as ``{old_word}`` in the list")


def setup(client):
    client.add_cog(Moderation(client))
