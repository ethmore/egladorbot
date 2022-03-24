import nextcord
from nextcord import Interaction
from nextcord.ext import commands
# from numpy import source
from youtube_dl import *
from nextcord import FFmpegPCMAudio
from youtubesearchpython import VideosSearch

queues = {}
commandPrefix = '.'
# testline
# testline
# testline
# testline
# testline
# testline

def checkQueue(ctx, id):
    if queues[id]:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        voice.play(source, after=lambda x=0: checkQueue(ctx, ctx.message.guild.id))


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


class Player(commands.Cog):
    def __init__(self, client):
        self.client = client

    testServerId = 643857272216354866
    egladorid = 340277764907204608
    

    @nextcord.slash_command(name="play2", description="plays", guild_ids=[testServerId, egladorid])
    async def splay(self, interaction: Interaction):
        player_pause = PlayerPause()
        #player_resume = PlayerResume()
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
                #player_pause = PlayerPause()
                await interaction.edit_original_message(view=player_pause)
                await player_pause.wait()
                return

    # Join a voice channel
    @commands.command(brief="Connects to a voice channel", pass_context=True)
    async def join(self, ctx):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            if ctx.author.voice:
                channel = ctx.message.author.voice.channel
                await channel.connect()
                await ctx.send(f'Connected to ``{channel}``')

            else:
                await ctx.send("Join a channel first")

    # Leave the voice channel
    @commands.command(brief="Disconnects from the voice channel", pass_context=True)
    async def leave(self, ctx):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            if ctx.voice_client:
                await ctx.guild.voice_client.disconnect()
                await ctx.send("Disconnected from the channel")
            else:
                await ctx.send("Not in a voice channel")
        else:
            pass

    # WIP - connect play, queue, resume
    @commands.command(brief="Resumes, Starts")
    async def play(self, ctx, url=None):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
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

                if url is not None:  # URL Parameter provided
                    if not url.startswith("https:"):
                        videosSearch = VideosSearch(url, limit=1)
                        res = videosSearch.result()
                        url = res['result'][0]['link']

                    if not voice.is_playing():  # Bot connected to a voice channel but not playing.

                        if url.startswith("https://www.youtube.com/playlist?list"):  # Eger link playlist ise
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

                                source = (FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

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

                                source = (FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

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
                            source = (FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

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

            else:
                await ctx.send("Join a channel first")
    """
    @nextcord.slash_command(name="play", description="Plays audio via given link or keywords", guild_ids=[testServerId, egladorid])
    async def play(self, interaction: Interaction, url):
        channel = self.client.get_channel(interaction.channel.id)
        if channel.name == 'bot-commands':
            if interaction.user.voice:
                YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
                FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

                vc = interaction.user.voice.channel
                voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

                if voice is None:  # Bot not connected to a voice channel
                    await vc.connect()
                    await interaction.send(f'Connected to ``{vc}``')
                    # await interaction.response.send_message(f'Connected to ``{vc}``', ephemeral=False)
                    voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

                if url is not None:  # URL Parameter provided
                    if not url.startswith("https:"):
                        videosSearch = VideosSearch(url, limit=1)
                        res = videosSearch.result()
                        url = res['result'][0]['link']

                    if not voice.is_playing():  # Bot connected to a voice channel but not playing.

                        if url.startswith("https://www.youtube.com/playlist?list"):  # Eger link playlist ise
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

                                source = (FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                                if not voice.is_playing():
                                    voice.play(source)
                                    voice.is_playing()

                                guild_id = interaction.message.guild.id
                                if guild_id in queues:
                                    queues[guild_id].append(source)
                                else:
                                    queues[guild_id] = [source]
                            await interaction.send(f"``{audioCounter}`` Audio added to the queue", delete_after=5)
                            await interaction.delete_original_message(delay=10)

                        else:
                            with YoutubeDL(YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(url, download=False)
                            URL = info['formats'][0]['url']
                            source = await nextcord.FFmpegOpusAudio.from_probe(URL, **FFMPEG_OPTIONS)
                            voice.play(source, after=lambda x=None: checkQueue(interaction, interaction.message.guild.id))
                            voice.is_playing()
                            await interaction.send(f"Playing: ``{info.get('title')}``")

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

                                source = (FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                                if not voice.is_playing():
                                    voice.play(source)
                                    voice.is_playing()

                                guild_id = interaction.message.guild.id
                                if guild_id in queues:
                                    queues[guild_id].append(source)
                                else:
                                    queues[guild_id] = [source]
                            await interaction.send(f"``{audioCounter}`` Audio added to the queue")

                        else:
                            # voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
                            with YoutubeDL(YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(url, download=False)
                            URL = info['formats'][0]['url']
                            source = (FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

                            guild_id = interaction.message.guild.id
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
    """
    # Pauses the player
    @commands.command(brief="Pauses the audio")
    async def pause(self, ctx):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice.is_playing():
                voice.pause()
            else:
                await ctx.send("There's no audio playing")

    # Resumes the player
    @commands.command(brief="Resumes the audio")
    async def resume(self, ctx):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice.is_paused():
                voice.resume()
            else:
                await ctx.send("There's no audio that paused!")

    # Skips the current audio
    @commands.command(brief="Skips the current audio")
    async def skip(self, ctx):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice.is_playing():
                try:
                    voice.pause()
                    source = queues[ctx.message.guild.id].pop(0)
                    voice.play(source, after=lambda x=None: checkQueue(ctx, ctx.message.guild.id))
                    voice.is_playing()
                    await ctx.send("Audio skipped!")
                except:
                    await ctx.send("Queue is empty!")
            else:
                await ctx.send("There's no audio playing!")

    # Stops the player
    @commands.command(brief="Stops the audio")
    async def stop(self, ctx):
        channel = self.client.get_channel(ctx.channel.id)
        if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice is None:
                await ctx.send("Bot is not in a voice channel")

            elif voice.is_playing():
                voice.stop()
                await ctx.guild.voice_client.disconnect()
                await ctx.send("Left from the channel")

            else:
                await ctx.send("There's no audio playing")

    # Play Enter the East
    @commands.command(brief="Taste of music", pass_context=True)
    async def ete(self, ctx):
        if ctx.author.voice:
            channel = self.client.get_channel(ctx.channel.id)
            if channel.name == 'bot-commands' and ctx.prefix is commandPrefix:
                await ctx.send("Taste of music!")
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
                source = FFmpegPCMAudio('ete.mp3')
                voice.play(source)


def setup(client):
    client.add_cog(Player(client))
