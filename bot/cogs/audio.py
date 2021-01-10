import youtube_dl
import os
import asyncio
import itertools
import discord
import random


from async_timeout import timeout
from functools import partial
from common.json_h import *
from common import config_h
from discord.ext import commands

"""
Variables
"""
conf = config_h.get()
ffmpeg_options = conf['ffmpeg_options']
ffmpeg_before_options = conf['ffmpeg_before_options']
ytdl = youtube_dl.YoutubeDL(conf['ytdlFormatOptions'])

class SongList():
    def __init__(self, audioJsonPath, audiopath):
        print(audiopath)
        self.audiopath = audiopath
        self.audioJsonPath = audioJsonPath
        audioSongsJson = self.importAudioJSON()
        audioSongsFiles = self.importAudioFiles()
        self.songs = self.mergeAudioLists(audioSongsJson, audioSongsFiles)
        self.exportAudioJson()

    def importAudioJSON(self):
        songs = []
        if os.path.isfile(self.audioJsonPath):
            audioList = get_json(self.audioJsonPath)
            for v in audioList:
                songs.append(Song(v['name'], v['category'], v['path'], v['aliases']))
            print('Songlist imported from {}'.format(self.audioJsonPath))
        return songs

    def exportAudioJson(self):
        strList = []
        for song in self.songs:
            strList.append(song.get_json())
        save_json(strList, self.audioJsonPath)

    def importAudioFiles(self):
        files = []

        #Reads all audio-files added to client-files
        # r=root, d=directories, f = files
        for r,d,f in os.walk(self.audiopath):
            for file in f:
                if file.endswith('.mp3'):
                    path = os.path.join(r, file)
                    path = os.path.normpath(path)
                    files.append(path[(len(self.audiopath) + 1):])
        #Creating dict of song-objects
        songs = []
        for f in files:
            name = os.path.basename(f).replace('.mp3','')
            songs.append(Song(name.lower(), os.path.dirname(f), f, [name.lower(), f.lower()]))

        return songs

    def mergeAudioLists(self, list1, list2):
        resultlist = list(list1)
        for song in list2:
            if song not in resultlist:
                print(song.get_json())
                resultlist.append(song)

        print('Songlists have been merged')
        return resultlist

    # Adds an alias to a song object
    # Will check if the alias is already in use somewhere else first
    # Returns a boolean indicating if alias was added
    def addAlias(self, name, newAlias):
        songDict = self.getSongDict()
        if newAlias in songDict:
            return False
        for i in range(0, len(self.songs)):
            if self.songs[i].name == name:
                self.songs[i].aliases.append(newAlias)
                self.exportAudioJson()
                return True
        return False

    # Returns a Song-object list of songs in a given category
    #
    # [{"name":"songname", "category":"folder", "filepath":"folder/file.mp3", "aliases":["file", "song", "retard"]}]
    def getListCategory(self, category=''):
        resultlist = []
        for song in self.songs:
            if song.getCategory() == category:
                resultlist.append(song)
        return resultlist

    # Returns a String list of categories
    # Each category is decided based on if it's in a subfolder under media
    # ["category1", "category2"]
    def getStrListCategories(self):
        resultlist = []
        for song in self.songs:
            cat = song.getCategory()
            if cat != '':
                if cat not in resultlist:
                    resultlist.append(cat)
        return resultlist

    # Returns a dictionary containing all aliases and corresponding filepaths.
    # Notice this might contain several entries pr. file
    # {"song":"path.mp3", "song.mp3":"path.mp3"}
    def getSongDict(self):
        resultdict = {}
        for song in self.songs:
            for alias in song.aliases:
                resultdict[alias] = song.getFilepath()
        return resultdict


class Song():
    def __init__(self, name, category, filepath, aliases):
        self.name = name
        self.category = category
        self.filepath = filepath
        self.aliases = aliases

    def __eq__(self, other):
        if not isinstance(other, Song):
            return NotImplemented
        if self.filepath == other.filepath:
            return True
        else:
            return False

    def get_json(self):
        return {"name": self.name, "category": self.category, "path": self.filepath, "aliases": self.aliases}

    def setAliases(self, aliases):
        self.aliases = aliases

    def getCategory(self):
        #return os.path.dirname(self.name)
        returnself.category

    def getBasename(self):
        #return os.path.basename(self.name)
        return self.name

    def getFilepath(self):
        return self.filepath


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md


    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)


    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send('```ini\n[Added {} to the Queue.]\n```'.format(data["title"]), delete_after=15)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        #Testing return cls(discord.FFmpegPCMAudio(source, options=ffmpeg_options, before_options=ffmpeg_before_options), data=data, requester=ctx.author)
        return cls(discord.FFmpegPCMAudio(source, options=ffmpeg_options, before_options=ffmpeg_before_options), data=data, requester=ctx.author)


    @classmethod
    async def create_source_local(cls, ctx, path, title, loop, notifyQueue=True):
        loop = loop or asyncio.get_event_loop()
        #Metadata for audiofile
        data = {'title':title}
        source = discord.FFmpegPCMAudio(path)

        #Don't notify to channel if an entire playlist is being added
        if notifyQueue:
            await ctx.send('```ini\n[Added {} to the Queue.]\n```'.format(data["title"]), delete_after=15)

        return cls(source, data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url'], options=ffmpeg_options, before_options=ffmpeg_before_options), data=data, requester=requester)

class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('client', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.client = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.client.wait_until_ready()

        while not self.client.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.client.loop)
                except Exception as e:
                    print(e)
                    await self._channel.send('There was an error processing your song.\n'
                                             '```css\n[{}]\n```'.format(e))
                    continue


            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.client.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send('**Now Playing:** `{}` requested by `{}`'.format(source.title, source.requester))
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.client.loop.create_task(self._cog.cleanup(guild))

class Audio(commands.Cog):
    __slots__ = ('client', 'players')

    def __init__(self, client):
        audiofilesPath = os.path.abspath(os.path.join(__file__ , "../../../media"))
        audioJsonPath = os.path.join(config_h.CONFIG_PATH, 'audio.json')

        self.client = client
        self.players = {}
        self.songlist = SongList(audioJsonPath, audiofilesPath)
        self.audiofilesPath = audiofilesPath

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    #
    # COMMANDS
    #

    @commands.command(name='connect', aliases=['join'])
    async def connect(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send('```css\n[ No channel to join. Please either specify a valid channel or join one. ]\n```', delete_after=20)
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError('Moving to channel: {} timed out.'.format(channel))
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError('Connecting to channel: {} timed out.'.format(channel))

        await ctx.send('Connected to: {}'.format(channel), delete_after=20)


    @commands.command(name='stream', aliases=['yt'])
    async def stream(self, ctx, *, search: str):
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        await ctx.trigger_typing()
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.connect)
        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.client.loop, download=False)

        await player.queue.put(source)

    @commands.command(name='play', aliases=['local'])
    async def play(self, ctx, *, query):

        await ctx.trigger_typing()
        queryLower = query.lower()

        songDict = self.songlist.getSongDict()
        categoryList = self.songlist.getStrListCategories()

        #Only connect if song or list exists
        if queryLower in categoryList or queryLower in songDict:
            # connects to voicechat if not already in it
            player = self.get_player(ctx)
            vc = ctx.voice_client
            if not vc:
                await ctx.invoke(self.connect)

        # If a category name is given, it will play song in category in random order
        if queryLower in categoryList:
            songs = self.songlist.getListCategory(queryLower)
            listSongs = list(songs)
            random.shuffle(listSongs)
            print('Requested list {}'.format(query))
            for song in listSongs:
                path = os.path.join(self.audiofilesPath, song.getFilepath())
                source = await YTDLSource.create_source_local(ctx, path, song.getBasename(), loop=self.client.loop, notifyQueue=False)
                await player.queue.put(source)

        # If songname or alias for song is given, that single song will be played
        elif queryLower in songDict:
            path = os.path.join(self.audiofilesPath, songDict[queryLower])
            print('Requested song {}'.format(path))
            source = await YTDLSource.create_source_local(ctx, path, query, loop=self.client.loop)
            await player.queue.put(source)

        # If not found in categories nor songaliases
        else:
            await ctx.send('Could not find {}'.format(query))


    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send('**{}**: Paused the song!'.format(ctx.author))

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send('**{}**: Resumed the song!'.format(ctx.author))

    @commands.command(name='skip')
    async def skip(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send('**{}**: Skipped the song!'.format(ctx.author))

    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('There are currently no more queued songs.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join('**{}**'.format(_["title"]) for _ in upcoming)
        embed = discord.Embed(title='Upcoming - Next {}'.format(len(upcoming)), description=fmt)

        await ctx.send(embed=embed)


    @commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
    async def now_playing(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('I am not currently playing anything!')

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send('**Now Playing:** {}\n requested by {}'.format(vc.source.title, vc.source.requester))



    @commands.command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: float):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send('**`{}`**: Set the volume to **{}%**'.format(ctx.author, vol))



    @commands.command(name='stop', aliases=['disconnect', 'dc'])
    async def stop(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)

        await self.cleanup(ctx.guild)



    @commands.command(name='categories', aliases=['cat', 'category'], description="Lists out all available categories (Not all songs a categorized)")
    async def categories(self, ctx):
        categoryList = self.songlist.getStrListCategories()

        fmt = '\n'.join('**{}**'.format(category) for category in categoryList)
        embed = discord.Embed(title='Categories', description=fmt)

        await ctx.send(embed=embed)


    @commands.command(name='songs', aliases=['category-songs'], description="Lists out songs in a given category")
    async def songs(self, ctx, category=None):
        songs = self.songlist.getListCategory()
        if not category:
            category = "No Category"

        fmt = '\n'.join('**{}** - {}'.format(song.name, song.aliases) for song in songs)
        embed = discord.Embed(title='Songs {} - aliases'.format(category), description=fmt)

        await ctx.send(embed=embed)

#
# SETUP
#

def setup(client):
    client.add_cog(Audio(client))
