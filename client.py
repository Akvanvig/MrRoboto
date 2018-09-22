#API-dokumentasjon:
#https://discordpy.readthedocs.io/en/latest/api.html
import random
import time, sched
import json
from datetime import datetime
from discord.ext import commands

reminders = []
remindersPlassering = './reminders.json'

botPrefix = ('&', '=')
client = commands.Bot(command_prefix = botPrefix)

#----------------------------------------------------------------------------------------------------------------------
#
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_member_remove(member):
    client.send_message(member.server.default_channel, member.name + ' has left the server.')

#--------------------------------------------------------------------------------------------------------------------
#Legg til fuck, marry kill (tar tilfeldige navn fra discord-serveren)
#Kommandoer
@client.command(name='8ball',
                description='Svarer på ja/nei spørsmål.',
                brief='Responderer på spørsmål.',
                aliases=['eigth_ball', 'eigthball', '8-ball'],
                pass_context=True)
async def eigth_ball(context):
    possibleResponses = [
        'Det er et klart nei',
        'Ser svært lite sannsynelig ut',
        'Vanskelig å si',
        'Det er godt mulig',
        'Definitivt'
    ]
    await client.say(random.choice(possibleResponses) + ', ' + context.message.author.mention)

@client.command(name='Reminder',
                description='Brukes "Reminder [ant tidsenhet] [tidsenhet] [melding]", implementerte tidsenheter: m/min/minutt, t/h/timer/hours, d/dag/dager/day/days',
                brief='Gir deg påminnelser etter angitt tid.',
                aliases=['reminder', 'REMINDER','påminnelse','Påminnelse','PÅMINNELSE'],
                pass_context=True,)
async def Reminder(context):
    text = context.message.content.split(' ')
    text.pop(0) #[0] ant tidsenhet, [1] tidsenhet, [2-*] melding
    avsenderId = context.message.author.id
    tid = context.message.timestamp
    channelId = context.message.channel.id

    if not text[0].isdigit():
        await client.say('Det ble ikke angitt noen tid')
        return

    #Beregner tid frem i tid
    enhet = text[1].lower()
    sek = 0
    if enhet == 'm' or enhet == 'min' or enhet == 'minutt':
        sek = int(text[0]) * 60
        enhet = 'minutt(er)'
        melding = ' '.join(text[2:])
    elif enhet == 't' or enhet == 'timer' or enhet == 'h' or enhet == 'hours':
        sek = int(text[0]) * 60 * 60
        enhet = 'time(r)'
        melding = ' '.join(text[2:])
    elif enhet == 'd' or enhet == 'dager' or enhet == 'dag' or enhet == 'day' or enhet == 'days':
        sek = int(text[0]) * 24 * 60 * 60
        enhet = 'dag(er)'
        melding = ' '.join(text[2:])
    else:   #Velger minutt om ikke annet er oppgitt
        sek = int(text[0]) * 60
        enhet = 'minutt(er)'
        melding = ' '.join(text[2:])

    fullfortTid = time.mktime(tid.timetuple()) + sek
    reminders.append(dict(fullfortTid=fullfortTid,avsenderId=avsenderId,channelId=channelId,melding=melding))
    saveJson(reminders, remindersPlassering)
    await client.say('Et varsel ble satt opp om {} {}'.format(text[0],enhet))

#Ikke implementert
@client.command(name='play',
                description='Spiller av Youtube-videoer til')
async def play():
    i = 0


#Adis Discord-poll prosjekt (Ikke implementert)
@client.command(name='poll',
                desciption='Oppretter en spørreundesøkelse på discord',
                brief='',
                aliases=['undersøkelse', 'Undersøkelse', 'Poll'],
                pass_context=True)
async def poll(context):
    pass

#--------------------------------------------------------------------------------------------------------
#Funksjoner
def saveJson(obj, sti):
    with open(sti, 'w') as fout:
        json.dump(obj, fout)

def getJson(sti):
    with open(sti, 'r') as fout:
        return json.load(fout)


#---------------------------------------------------------------------------------------------------------
#Oppstart
try:
    reminders = getJson(remindersPlassering)
except Exception as e:
    print(e)

username = ''
password = ''
client.run(username, password)
#token = ''
#client.run(token)
