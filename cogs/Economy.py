import nextcord
from nextcord.ext import commands
import json
import re
import random
import config

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def addcoin(self, ctx, member: nextcord.Member, amount):
        await ctx.send("WIP")

    @commands.command(brief="`` {config.commandPrefix}coinflip `tails / heads` ``")
    async def coinflip(self, ctx, guess=None):
        flip_list = ["heads", "tails"]
        result = random.choice(flip_list)
        if guess is None:
            await ctx.send(f"`` {config.commandPrefix}coinflip `tails / heads` ``")
        else:
            if result == guess:
                await ctx.send("True")
            else:
                await ctx.send("Wrong")


def setup(client):
    client.add_cog(Economy(client))
