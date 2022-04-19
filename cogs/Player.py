import nextcord
import youtube_dl.utils
from nextcord import Interaction
from nextcord.ext import commands
from youtube_dl import *
from youtubesearchpython import VideosSearch
import config
import asyncio
import time

queues = {}


def checkQueue(ctx, q_id):
    try:
        if queues[q_id]:
            voice = ctx.guild.voice_client
            source = queues[q_id].pop(0)
            voice.play(source, after=lambda x=0: checkQueue(ctx, ctx.message.guild.id))
    except KeyError:
        pass


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


class Player(commands.Cog):
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
    async def slash_join(self, interaction: Interaction):
        if interaction.user.voice.channel:
            if not interaction.guild.voice_client:
                channel = interaction.user.voice.channel
                await channel.connect()
                await interaction.send(f'Connected to ``{channel}``')

                voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
                while voice.is_playing():
                    await asyncio.sleep(30)
                else:
                    await asyncio.sleep(60)
                    while voice.is_playing():
                        break
                    else:
                        await voice.disconnect()

            else:
                await interaction.send("Already connected to a voice channel")
                pass

        else:
            await interaction.send("Join a voice channel first")

    @nextcord.slash_command(name="leave", description="Disconnects from the voice channel", guild_ids=config.guildID)
    async def slash_leave(self, interaction: Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect(force=True)
            await interaction.send("Disconnected from the channel")
        else:
            await interaction.send("Not in a voice channel")

    @nextcord.slash_command(name="play", description="Plays audio via given link or keywords", guild_ids=config.guildID)
    async def slash_play(self, interaction: Interaction, input):
        if interaction.user.voice.channel:
            YDL_OPTIONS = {'format': 'bestaudio/best',
                           'noplaylist': True,
                           'nocheckcertificate': True,
                           'quiet': True,}
            # YDL_OPTIONS = {'format': 'bestaudio/best',
            #                'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            #                'restrictfilenames': True,
            #                'noplaylist': True,
            #                'nocheckcertificate': True,
            #                'ignoreerrors': False,
            #                'logtostderr': False,
            #                'quiet': False,
            #                'no_warnings': True,
            #                'default_search': 'auto',
            #                'source_address': '0.0.0.0'
            #                }
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            # FFMPEG_OPTIONS = {'options': '-vn'}

            vc = interaction.user.voice.channel
            voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

            if voice is None:  # Bot not connected to a voice channel
                await vc.connect()
                await interaction.send(f'Connected to ``{vc}``')
                voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

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

                        source = (nextcord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                        if not voice.is_playing():
                            voice.play(source)
                            voice.is_playing()

                        guild_id = interaction.guild_id
                        if guild_id in queues:
                            queues[guild_id].append(source)
                        else:
                            queues[guild_id] = [source]
                    channel = self.client.get_channel(interaction.channel.id)
                    await channel.send(f"``{audioCounter}`` Audio added to the queue", delete_after=5)

                else:
                    try:
                        localtime = time.localtime(time.time())
                        print("Local current time :", localtime)

                        with YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(input, download=False)
                        URL = info['formats'][0]['url']
                        source = await nextcord.FFmpegOpusAudio.from_probe(URL, **FFMPEG_OPTIONS)

                        try:
                            voice.play(source, after=lambda x=None: checkQueue(interaction, interaction.guild_id))
                        except KeyError:
                            pass
                    except youtube_dl.utils.DownloadError as msg:
                        await interaction.send(f"{msg}")
                        pass

                    localtime = time.localtime(time.time())
                    print("Local current time :", localtime)
                    voice.is_playing()
                    try:
                        await interaction.send(f"Playing: ``{info.get('title')}``")
                    except nextcord.errors.NotFound:
                        channel = self.client.get_channel(interaction.channel.id)
                        await channel.send(f"Playing: ``{info.get('title')}``")

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

                        source = (nextcord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                        if not voice.is_playing():
                            voice.play(source)
                            voice.is_playing()

                        guild_id = interaction.guild_id
                        if guild_id in queues:
                            queues[guild_id].append(source)
                        else:
                            queues[guild_id] = [source]
                    channel = self.client.get_channel(interaction.channel.id)
                    await channel.send(f"``{audioCounter}`` Audio added to the queue")

                else:
                    # voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
                    with YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(input, download=False)
                    URL = info['formats'][0]['url']
                    source = (nextcord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                    guild_id = interaction.guild_id
                    if guild_id in queues:
                        queues[guild_id].append(source)
                    else:
                        queues[guild_id] = [source]
                    await interaction.send(f"``{info.get('title')}`` Added to the queue")

            while voice.is_playing():
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(60)
                while voice.is_playing():
                    break
                else:
                    await voice.disconnect()

        else:
            await interaction.send("Join a channel first")

    @nextcord.slash_command(name="pause", description="Pauses the audio", guild_ids=config.guildID)
    async def slash_pause(self, interaction: Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice.is_playing():
            voice.pause()
            await interaction.send("Player paused")
        else:
            await interaction.send("There's no audio playing")

    @nextcord.slash_command(name="resume", description="Resumes the audio", guild_ids=config.guildID)
    async def slash_resume(self, interaction: Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice.is_paused():
            voice.resume()
            await interaction.send("Player resumed")
        else:
            await interaction.send("There's no audio paused!")

    @nextcord.slash_command(name="skip", description="Skips the current audio", guild_ids=config.guildID)
    async def slash_skip(self, interaction: Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice is None:
            await interaction.send("Bot is not in a voice channel")
        else:
            if voice.is_playing():
                try:
                    voice.pause()
                    source = queues[interaction.guild_id].pop(0)
                    voice.play(source, after=lambda x=None: checkQueue(interaction, interaction.guild_id))
                    voice.is_playing()
                    await interaction.send("Audio skipped!")
                except IndexError:
                    voice.stop()
                    print("IndexError")
                    await interaction.send("Queue is emptied!")
                except KeyError:
                    voice.stop()
                    print("KeyError")
                    await interaction.send("Queue is emptied!`")

            else:
                await interaction.send("There's no audio playing!")

    @nextcord.slash_command(name="stop", description="Stops the audio", guild_ids=config.guildID)
    async def slash_stop(self, interaction: Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice is None:
            await interaction.send("Bot is not in a voice channel")

        elif voice.is_playing():
            guild_id = interaction.guild_id
            if guild_id in queues:
                queues.pop(guild_id)
            voice.stop()
            await interaction.send("Player is stopped")

        else:
            await interaction.send("There's no audio playing")

    @nextcord.slash_command(name="ete", description="Taste of music", guild_ids=config.guildID)
    async def slash_ete(self, interaction: Interaction):
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

    # Prefix commands

    # Join a voice channel
    @commands.command(brief="Connects to a voice channel", pass_context=True)
    async def join(self, ctx):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            if ctx.author.voice:

                channel = ctx.message.author.voice.channel
                await channel.connect()
                await ctx.send(f'Connected to ``{channel}``')
                voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)

                while voice.is_playing():
                    await asyncio.sleep(30)
                else:
                    await asyncio.sleep(60)
                    while voice.is_playing():
                        break
                    else:
                        await voice.disconnect()

    # Leave the voice channel
    @commands.command(brief="Disconnects from the voice channel", pass_context=True)
    async def leave(self, ctx):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            if ctx.voice_client:
                await ctx.guild.voice_client.disconnect()
                await ctx.send("Disconnected from the channel")
            else:
                await ctx.send("Not in a voice channel")
        else:
            pass

    # WIP - connect play, queue, resume
    @commands.command(brief="Resumes, Starts")
    async def play(self, ctx, *args):
        await config.allowMsg(ctx.message)
        url = ""
        for keyword in args:
            url = url + keyword + " "

        if config.allowMessages is True:
            if ctx.author.voice:
                YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
                FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

                author = ctx.message.author
                vc = author.voice.channel
                voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)

                if voice is None:  # Bot not connected to a voice channel
                    await vc.connect()
                    await ctx.send(f'Connected to ``{vc}``')
                    voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)

                if url != "":  # URL Parameter provided
                    if not url.startswith("https:"):
                        videosSearch = VideosSearch(url, limit=1)
                        res = videosSearch.result()
                        url = res['result'][0]['link']

                    if not voice.is_playing():  # Bot connected to a voice channel but not playing.

                        if url.startswith("https://www.youtube.com/playlist?list"):  # If link belongs to a playlist
                            audioCounter = 0
                            YDL_OPTIONS = {'format': 'bestaudio', 'extract_flat': 'in_playlist'}
                            with YoutubeDL(YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(url, download=False)

                            for entry in info['entries']:
                                audioCounter += 1
                                VidId = entry['id']
                                url = f"https://www.youtube.com/watch?v={VidId}"

                                with YoutubeDL(YDL_OPTIONS) as ydl:
                                    info = ydl.extract_info(url, download=False)
                                URL = info['formats'][0]['url']

                                source = (nextcord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                                if not voice.is_playing():
                                    voice.play(source)
                                    voice.is_playing()

                                guild_id = ctx.message.guild.id
                                if guild_id in queues:
                                    queues[guild_id].append(source)
                                else:
                                    queues[guild_id] = [source]
                            await ctx.send(f"``{audioCounter}`` Audio added to the queue")

                        else:
                            with YoutubeDL(YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(url, download=False)
                            URL = info['formats'][0]['url']
                            source = await nextcord.FFmpegOpusAudio.from_probe(URL, **FFMPEG_OPTIONS)
                            voice.play(source, after=lambda x=None: checkQueue(ctx, ctx.message.guild.id))
                            voice.is_playing()
                            await ctx.send(f"Playing: ``{info.get('title')}``")

                    elif voice.is_playing():

                        if url.startswith("https://www.youtube.com/playlist?list"):
                            YDL_OPTIONS = {'format': 'bestaudio', 'extract_flat': 'in_playlist'}  #
                            audioCounter = 0

                            with YoutubeDL(YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(url, download=False)

                            for entry in info['entries']:
                                audioCounter += 1
                                VidId = entry['id']
                                url = f"https://www.youtube.com/watch?v={VidId}"

                                with YoutubeDL(YDL_OPTIONS) as ydl:
                                    info = ydl.extract_info(url, download=False)
                                URL = info['formats'][0]['url']

                                source = (nextcord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                                if not voice.is_playing():
                                    voice.play(source)
                                    voice.is_playing()

                                guild_id = ctx.message.guild.id
                                if guild_id in queues:
                                    queues[guild_id].append(source)
                                else:
                                    queues[guild_id] = [source]
                            await ctx.send(f"``{audioCounter}`` Audio added to the queue")

                        else:
                            # voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
                            with YoutubeDL(YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(url, download=False)
                            URL = info['formats'][0]['url']
                            source = (nextcord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                            guild_id = ctx.message.guild.id
                            if guild_id in queues:
                                queues[guild_id].append(source)
                            else:
                                queues[guild_id] = [source]
                            await ctx.send(f"``{info.get('title')}`` Added to the queue")

                else:
                    if voice.is_paused():
                        voice.resume()
                        await ctx.send("Player resumed")
                    else:
                        await ctx.send("Provide a link or keyword/s")

                while voice.is_playing():
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(60)
                    while voice.is_playing():
                        break
                    else:
                        await voice.disconnect()

            else:
                await ctx.send("Join a channel first")

    # Pauses the player
    @commands.command(brief="Pauses the audio")
    async def pause(self, ctx):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice.is_playing():
                voice.pause()
            else:
                await ctx.send("There's no audio playing")

    # Resumes the player
    @commands.command(brief="Resumes the audio")
    async def resume(self, ctx):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice.is_paused():
                voice.resume()
            else:
                await ctx.send("There's no audio that paused!")

    # Skips the current audio
    @commands.command(brief="Skips the current audio")
    async def skip(self, ctx):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice is None:
                await ctx.send("Bot is not in a voice channel")
            else:
                if voice.is_playing():
                    try:
                        voice.pause()
                        source = queues[ctx.message.guild.id].pop(0)
                        voice.play(source, after=lambda x=None: checkQueue(ctx, ctx.message.guild.id))
                        voice.is_playing()
                        await ctx.send("Audio skipped!")
                    except IndexError:
                        voice.stop()
                        await ctx.send("Queue is emptied!")
                    except KeyError:
                        voice.stop()
                        await ctx.send("Queue is emptied!`")

                else:
                    await ctx.send("There's no audio playing!")

    # Stops the player
    @commands.command(brief="Stops the audio")
    async def stop(self, ctx):
        await config.allowMsg(ctx.message)
        if config.allowMessages is True:
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice is None:
                await ctx.send("Bot is not in a voice channel")

            elif voice.is_playing():
                voice.stop()
                await ctx.send("Player is stopped")

            else:
                await ctx.send("There's no audio playing")


def setup(client):
    client.add_cog(Player(client))
