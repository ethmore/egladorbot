import nextcord
from nextcord.ext import commands


class Greet(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Member greeting
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.client.get_channel(643867765983150100)
        await channel.send("Hello")

    # Member sendoff
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.client.get_channel(643867765983150100)
        await channel.send("Bye")


def setup(client):
    client.add_cog(Greet(client))
