#API-dokumentasjon:
#https://discordpy.readthedocs.io/en/latest/api.html
import random
from discord.ext import commands

botPrefix = ('&', '?')
client = commands.Bot(command_prefix = botPrefix)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_member_remove(member):
    client.send_message(member.server.default_channel, member.name + ' has left the server.')

#Kommandoer
@client.command(name='8ball',
                description='Svarer på ja/nei spørsmål.',
                breif='Responderer på spørsmål.',
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

username = ''
password = ''
client.run(username, password)
#token = ''
#client.run(token)
