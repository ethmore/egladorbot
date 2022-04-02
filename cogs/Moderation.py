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

        if config.channelSelectivity is True:   # Channel selectivity check
            if channel.name == config.selectedChannel and not message.content.startswith(config.commandPrefix) and message.author != self.client.user:
                await message.delete()  # Channel TRUE, prefix FALSE, message NOT belongs to the bot
                config.allowMessages = False
            elif channel.name != config.selectedChannel and message.content.startswith(config.commandPrefix) and message.author != self.client.user:
                await message.delete()  # Channel FALSE, prefix TRUE, message NOT belongs to the bot
                config.allowMessages = False
        else:
            config.allowMessages = False

    @nextcord.slash_command(name="test", description="Up Test", guild_ids=config.guildID)
    async def test(self, interaction: Interaction):
        await interaction.send("Online")

    # WIP - WIP - WIP - WIP - WIP - WIP
    @nextcord.slash_command(name="delete", description="[WIP] Deletes message", guild_ids=config.guildID)
    async def delete(self, interaction: Interaction):
        # author = ctx.message.author
        await interaction.message.delete()
        await interaction.send("Deleted [WIP]")


def setup(client):
    client.add_cog(Moderation(client))
