#API-dokumentasjon:
#https://discordpy.readthedocs.io/en/latest/api.html
import discord
from discord.ext import commands
import logging, os, json, asyncio, random

from functions import *
from audio import Music
from animations import Animations
from commands import Other


"""
Standard variables
"""
audiofilesPath = './media/audio/'
configPath = './config/'
audioJsonPath = '{}audio.json'.format(configPath)
configJsonPath = '{}config.json'.format(configPath)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)


"""
Loading config and creating example if missing
"""
createFolderIfNotExist(configPath)
createFolderIfNotExist(audiofilesPath)

if os.path.exists(configJsonPath):
    conf = getJson(configJsonPath)
    client = commands.Bot(command_prefix=conf['commandPrefix'], case_insensitive=True, owner_ids=conf['ownerIds'])
else:
    print('Missing config')
    exampleConf = {'discordToken':'fdjkakjdfefehsabh93,.3mejnfe', 'commandPrefix':'?', 'ownerIds':[] , 'ytdlFormatOptions': {'format': 'bestaudio/best','outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s', 'restrictfilenames': True, 'noplaylist': True, 'nocheckcertificate': True, 'ignoreerrors': False, 'logtostderr': False, 'quiet': True, 'no_warnings': True, 'default_search': 'auto', 'source_address': '0.0.0.0',"HighWaterMark":3145728}, 'ffmpeg_options':{'options': '-vn'},"ffmpeg_before_options":{"reconnect": 1, "reconnect_streamed": 1, "reconnect_delay_max":5}}
    saveJson(exampleConf, configJsonPath)


"""
Other Events
"""
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.author != client.user:
        print(message.content)
    await client.process_commands(message)



"""
Starting bot
"""
if os.path.exists(configJsonPath):
    client.add_cog(Music(client, audioJsonPath, audiofilesPath))
    client.add_cog(Animations(client))
    client.add_cog(Other(client))
    client.run(conf['discordToken'])
