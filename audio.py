import youtube_dl
import os, json
from functions import *

import discord
from discord.ext import commands

"""
Variables
"""
ytdl = {}

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
            audioList = getJson(self.audioJsonPath)
            for v in audioList:
                songs.append(Song(v['name'], v['path'], v['aliases']))
            print('Songlist imported from {}'.format(self.audioJsonPath))
        return songs

    def exportAudioJson(self):
        strList = []
        for song in self.songs:
            strList.append(song.getJson())
        saveJson(strList, self.audioJsonPath)

    def importAudioFiles(self):
        files = []

        #Reads all audio-files added to client-files
        # r=root, d=directories, f = files
        for r,d,f in os.walk(self.audiopath):
            for file in f:
                if file.endswith('.mp3'):
                    path = os.path.join(r, file)
                    path = path.replace('\\','/') #Replaces backslashes given by windows with a single regular slash
                    path = (path)[(len(self.audiopath)):] #Removes path listed to audio-directory
                    files.append(path)
        #Creating dict of song-objects
        songs = []
        for f in files:
            name = (f.replace('.mp3',''))
            songs.append(Song(name.lower(), f, [name.lower(), f.lower()]))

        return songs

    def mergeAudioLists(self, list1, list2):
        resultlist = list(list1)
        resultlist.extend(x for x in list2 if x not in resultlist)
        print('Songlists have been merged')
        return resultlist

    def addAlias(self, name, newAlias):
        aliasDict = self.getAliasDict()
        if newAlias in aliasDict:
            return False
        for i in range(0, len(self.songs)):
            if self.songs[i].name == name:
                if not newAlias in self.songs[i].aliases:
                    self.songs[i].aliases.append(newAlias)
                    self.exportAudioJson()
                    return True
                return False
        return False

    def getStrListCategory(self, category):
        resultlist = []
        for song in self.songs:
            if song.name.startswith(category):
                resultlist.append('{} - {}'.format(song.name, song.aliases))
        return resultlist

    def getStrListNoCategory(self):
        resultlist = []
        for song in self.songs:
            if '/' not in song.name:
                resultlist.append('{} - {}'.format(song.name, song.aliases))
        return resultlist

    def getStrListCategories(self):
        resultlist = []
        for song in self.songs:
            if '/' in song.name:
                category = (song.name.split('/'))[0]
                if category not in resultlist:
                    resultlist.append(category)
        return resultlist

    def getAliasDict(self):
        resultdict = {}
        for song in self.songs:
            for alias in song.aliases:
                resultdict[alias] = song.filepath
        return resultdict

class Song():
    def __init__(self, name, filepath, aliases):
        self.name = name
        self.filepath = filepath
        self.aliases = aliases

    def getJson(self):
        return {"name": self.name, "path": self.filepath, "aliases": self.aliases}

    def setAliases(self, aliases):
        self.aliases = aliases

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
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
        return cls(discord.FFmpegPCMAudio(filename, options=ffmpeg_options, before_options=ffmpeg_before_options), data=data)

class Music(commands.Cog):
    def __init__(self, client, audioJsonPath, audiofilesPath, ytdlFormatOptions):
        self.client = client
        self.songList = SongList(audioJsonPath, audiofilesPath)
        self.audiofilesPath = audiofilesPath
        ytdl = youtube_dl.YoutubeDL(ytdlFormatOptions)


    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()


    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        aliasDict = self.songList.getAliasDict()
        result = ''

        if query.lower() in aliasDict:
            path = self.audiofilesPath + aliasDict[query.lower()]
            print('Requested {}'.format(path))
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            result = 'Now playing: {}'.format(query)
        else:
            result = 'Could not find {}'.format(query)

        await ctx.send(result)


    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.client.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))


    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))


    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))


    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the client from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
