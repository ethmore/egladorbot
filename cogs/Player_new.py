# play by link is between   0,5-1 secs
# play by search is between 1.5-2 secs
# can play with url or by search

import nextcord
from nextcord import Interaction
from nextcord.ext import commands
import youtube_dl
import config
import asyncio
import time

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(nextcord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class PlayerNew(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="stream", description="stream the audio", guild_ids=config.guildID)
    async def stream(self, interaction: Interaction, *, url):
        vc = interaction.user.voice.channel
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice is None:  # Bot not connected to a voice channel
            await vc.connect()
            await interaction.send(f'Connected to ``{vc}``')
            voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

        localtime = time.localtime(time.time())
        print("Local current time :", localtime)

        player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
        voice.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        localtime = time.localtime(time.time())
        print("Local current time :", localtime)


def setup(client):
    client.add_cog(PlayerNew(client))
