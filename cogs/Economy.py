import nextcord
from nextcord.ext import commands
import json
import re


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def addcoin(self, ctx, member: nextcord.Member, amount):
       await ctx.send("WIP")


def setup(client):
    client.add_cog(Economy(client))
