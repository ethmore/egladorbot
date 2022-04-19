import nextcord
from nextcord.ext import commands
import random
import config
from nextcord import Interaction


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="add_coin", description="WIP", guild_ids=config.guildID)
    async def add_coin(self, interaction: Interaction, member: nextcord.Member, amount):
        await interaction.send(f"{member.mention} this feature is WIP")
        print(amount)

    @nextcord.slash_command(name="coinflip", description="`` {config.commandPrefix}coinflip `tails / heads` ``", guild_ids=config.guildID)
    async def coinflip(self, interaction: Interaction, guess=None):
        flip_list = ["heads", "tails"]
        result = random.choice(flip_list)
        if guess is None:
            await interaction.send(f"`` {config.commandPrefix}coinflip `tails / heads` ``")
        else:
            if result == guess:
                await interaction.send("True")
            else:
                await interaction.send("Wrong")


def setup(client):
    client.add_cog(Economy(client))
