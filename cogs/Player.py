import nextcord
from nextcord import Interaction
# from nextcord.ext import commands
from youtube_dl import *
from nextcord import FFmpegPCMAudio
from youtubesearchpython import VideosSearch
import config

queues = {}


def checkQueue(ctx, id):
    if queues[id]:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        voice.play(source, after=lambda x=0: checkQueue(ctx, ctx.message.guild.id))


"""
class PlayerButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label="Resume", style=nextcord.ButtonStyle.green)
    async def playButton(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message('Play button', ephemeral=False)
        self.value = True
        self.stop()

    @nextcord.ui.button(label="Pause", style=nextcord.ButtonStyle.red)
    async def pauseButton(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message('Pause button', ephemeral=False)
        self.value = False
        self.stop()


class PlayerResume(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label="Resume", style=nextcord.ButtonStyle.green)
    async def resumeButton(self, button: nextcord.ui.Button, interaction: Interaction):
        # await interaction.response.send_message('Play button', ephemeral=False)
        self.value = True
        self.stop()


class PlayerPause(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label="Pause", style=nextcord.ButtonStyle.red)
    async def pauseButton(self, button: nextcord.ui.Button, interaction: Interaction):
        # await interaction.response.send_message('Play button', ephemeral=False)
        self.value = True
        self.stop()
"""


class Player:
    def __init__(self, client):
        self.client = client
    """
    @nextcord.slash_command(name="play2", description="plays", guild_ids=config.guildID)
    async def splay(self, interaction: Interaction):
        player_pause = PlayerPause()
        # player_resume = PlayerResume()
        await interaction.response.send_message(view=player_pause)
        await player_pause.wait()
        player_resume = PlayerResume()
        if player_pause.value is None:
            return

        elif player_pause.value:
            print("pause")
            voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
            voice.pause()
            player_resume = PlayerResume()
            # await interaction.response.send_message(view=player_resume)
            await interaction.edit_original_message(view=player_resume)
            await player_resume.wait()

            if player_resume.value:
                print("play")
                voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
                voice.resume()
                # player_pause = PlayerPause()
                await interaction.edit_original_message(view=player_pause)
                await player_pause.wait()
                return
    """
    @nextcord.slash_command(name="join", description="Connects to a voice channel", guild_ids=config.guildID)
    async def join(self, interaction: Interaction):
        if interaction.user.voice.channel:
            if not interaction.guild.voice_client:
                channel = interaction.user.voice.channel
                await channel.connect()
                await interaction.send(f'Connected to ``{channel}``')

            else:
                await interaction.send("Already connected to a voice channel")
                pass

        else:
            await interaction.send("Join a voice channel first")

    @nextcord.slash_command(name="leave", description="Disconnects from the voice channel", guild_ids=config.guildID)
    async def leave(self, interaction: Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect(force=True)
            await interaction.send("Disconnected from the channel")
        else:
            await interaction.send("Not in a voice channel")

    @nextcord.slash_command(name="play", description="Plays audio via given link or keywords", guild_ids=config.guildID)
    async def play(self, interaction: Interaction, input):
        if interaction.user.voice.channel:
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

            vc = interaction.user.voice.channel
            voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

            if voice is None:  # Bot not connected to a voice channel
                await vc.connect()
                await interaction.send(f'Connected to ``{vc}``')
                # await interaction.response.send_message(f'Connected to ``{vc}``', ephemeral=False)
                voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

            if input is not None:  # URL Parameter provided
                if not input.startswith("https:"):
                    videosSearch = VideosSearch(input, limit=1)
                    res = videosSearch.result()
                    input = res['result'][0]['link']

                if not voice.is_playing():  # Bot connected to a voice channel but not playing.

                    if input.startswith("https://www.youtube.com/playlist?list"):  # If link belongs to a playlist
                        audioCounter = 0
                        YDL_OPTIONS = {'format': 'bestaudio', 'extract_flat': 'in_playlist'}
                        with YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(input, download=False)

                        for entry in info['entries']:
                            audioCounter += 1
                            VidId = entry['id']
                            input = f"https://www.youtube.com/watch?v={VidId}"

                            with YoutubeDL(YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(input, download=False)
                            URL = info['formats'][0]['url']

                            source = (FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                            if not voice.is_playing():
                                voice.play(source)
                                voice.is_playing()

                            guild_id = interaction.guild_id
                            if guild_id in queues:
                                queues[guild_id].append(source)
                            else:
                                queues[guild_id] = [source]
                        await interaction.send(f"``{audioCounter}`` Audio added to the queue", delete_after=5)
                        await interaction.delete_original_message(delay=10)

                    else:
                        with YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(input, download=False)
                        URL = info['formats'][0]['url']
                        source = await nextcord.FFmpegOpusAudio.from_probe(URL, **FFMPEG_OPTIONS)
                        voice.play(source, after=lambda x=None: checkQueue(interaction, interaction.guild_id))
                        voice.is_playing()
                        await interaction.send(f"Playing: ``{info.get('title')}``")

                elif voice.is_playing():

                    if input.startswith("https://www.youtube.com/playlist?list"):
                        YDL_OPTIONS = {'format': 'bestaudio', 'extract_flat': 'in_playlist'}  #
                        audioCounter = 0

                        with YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(input, download=False)

                        for entry in info['entries']:
                            audioCounter += 1
                            VidId = entry['id']
                            input = f"https://www.youtube.com/watch?v={VidId}"

                            with YoutubeDL(YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(input, download=False)
                            URL = info['formats'][0]['url']

                            source = (FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                            if not voice.is_playing():
                                voice.play(source)
                                voice.is_playing()

                            guild_id = interaction.guild_id
                            if guild_id in queues:
                                queues[guild_id].append(source)
                            else:
                                queues[guild_id] = [source]
                        await interaction.send(f"``{audioCounter}`` Audio added to the queue")

                    else:
                        # voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
                        with YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(input, download=False)
                        URL = info['formats'][0]['url']
                        source = (FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                        guild_id = interaction.guild_id
                        if guild_id in queues:
                            queues[guild_id].append(source)
                        else:
                            queues[guild_id] = [source]
                        await interaction.send(f"``{info.get('title')}`` Added to the queue")

            else:
                if voice.is_paused():
                    voice.resume()
                    await interaction.send("Player resumed")
                else:
                    await interaction.send("Provide a link or keyword/s")

        else:
            await interaction.send("Join a channel first")

    @nextcord.slash_command(name="pause", description="Pauses the audio", guild_ids=config.guildID)
    async def pause(self, interaction: Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice.is_playing():
            voice.pause()
            await interaction.send("Player paused")
        else:
            await interaction.send("There's no audio playing")

    @nextcord.slash_command(name="resume", description="Resumes the audio", guild_ids=config.guildID)
    async def resume(self, interaction: Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice.is_paused():
            voice.resume()
            await interaction.send("Player resumed")
        else:
            await interaction.send("There's no audio that paused!")

    @nextcord.slash_command(name="skip", description="Skips the current audio", guild_ids=config.guildID)
    async def skip(self, interaction: Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice.is_playing():
            try:
                voice.pause()
                source = queues[interaction.guild_id].pop(0)
                voice.play(source, after=lambda x=None: checkQueue(interaction, interaction.guild_id))
                voice.is_playing()
                await interaction.send("Audio skipped!")
            except:
                await interaction.send("Queue is empty!")
        else:
            await interaction.send("There's no audio playing!")

    @nextcord.slash_command(name="stop", description="Stops the audio", guild_ids=config.guildID)
    async def stop(self, interaction: Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice is None:
            await interaction.send("Bot is not in a voice channel")

        elif voice.is_playing():
            voice.stop()
            # await interaction.guild.voice_client.disconnect(force=True)
            await interaction.send("Player is stopped")

        else:
            await interaction.send("There's no audio playing")

    @nextcord.slash_command(name="ete", description="Taste of music", guild_ids=config.guildID)
    async def ete(self, interaction: Interaction):
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        if interaction.user.voice.channel:
            await interaction.send("Taste of music!")
            channel = interaction.user.voice.channel
            voice = await channel.connect()
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info('https://www.youtube.com/watch?v=bn1YCClRF-g', download=False)
            URL = info['formats'][0]['url']
            source = await nextcord.FFmpegOpusAudio.from_probe(URL, **FFMPEG_OPTIONS)
            voice.play(source, after=lambda x=None: checkQueue(interaction, interaction.message.guild.id))
            voice.is_playing()


def setup(client):
    client.add_cog(Player(client))
