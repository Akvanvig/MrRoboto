#API-dokumentasjon:
#https://discordpy.readthedocs.io/en/latest/api.html
import discord

import json
import os

from audio import *
from commands import *

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    async def on_message(self, message):
        if message.content.startswith('+'):
            cmd = message.content[1:].split(' ')[0].lower()
            audiocommand(cmd, message)
        elif message.content.startswith('?'):
            cmd = message.content[1:].split(' ')[0].lower()
            command(cmd, message)


#---------------------------------------------------------------------------------------------------------
#Funksjoner
def saveJson(obj, path):
    with open(path, 'w') as fout:
        json.dump(obj, fout)

def getJson(path):
    with open(path, 'r') as fout:
        return json.load(fout)

def importAudio():
    path = './media/audio/'
    files = []

    #Reads all audio-files added to bot-files
    # r=root, d=directories, f = files
    for r,d,f in os.walk(path):
        for file in f:
            if file.endswith('.mp3'):
                files.append(os.path.join(r, file))

    #fixes paths to remove unneccesary info and
    for i in range(0,len(files)):
        files[i] = files[i].replace('\\\\','/') #Replaces backslashes given by windows with a single regular slash
        files[i] = (files[i])[(len(path)):] #Removes path listed to audio-directory

    #Add all files to Audio-objects

#---------------------------------------------------------------------------------------------------------
client = MyClient()
token = getJson('./token.json')
client.run(token['discord'])
