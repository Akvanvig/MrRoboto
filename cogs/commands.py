import asyncio
import random
import discord

from discord.ext import commands

#
# CLASSES
#

class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Read reminder list from disk on_ready
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command()
    async def latency(self, ctx):
        await ctx.send("Bot latency is {:.2f} ms".format(self.client.latency))

    @commands.command()
    async def choose(self, ctx, *choices: str):
        await ctx.send('{} has been chosen'.format(random.choice(choices)))

    @commands.command()
    @commands.cooldown(
        rate = 1,
        per = 30.0,
        type = commands.BucketType.member)
    async def kys(self, ctx):
        async with ctx.typing():
            await asyncio.sleep(30)
            await ctx.send('What the fuck did you just fucking say about me, you little bitch? I’ll have you know I graduated top of my class in the Navy Seals, and I’ve been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I’m the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that’s just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little \'clever\' comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You’re fucking dead, kiddo.')

    @commands.command(
        name = "remindme")
    async def remind_me(self, ctx, *time):
        pass

    @commands.command()
    async def credits(self, ctx):
        print('invoked')
        users = [
            {"title":"**Lead Project Manager** & **Chief Systems Architect**", "name":"**Adis Pinjic**"},
            {"title":"**Chief Orkitect** & **Grand Master of the Memologists**", "name":"**Eirik 'El Lolando' Andersen**"},
            {"title":"**Chancellor of the Code** & **President of Marketing**", "name":"**Andreas 'Esteban' Hennestad**"},
            {"title":"**Head Officer of Security** & **Drug Dealer**", "name":"**Mikkel '天皇' Thoresen**"},
            {"title":"code-monkeys", "name":"Anders & Fredrico"}
        ]
        lenTitle = len(max([i['title'] for i in users], key=len))
        lenName = len(max([i['name'] for i in users], key=len))
        fmt = '\n'.join("{0:>{1}} -- {2:{3}}".format(_["title"], lenTitle, _["name"], lenName) for _ in users)
        embed = discord.Embed(title='Credits', description=fmt)

        await ctx.send(embed=embed)

#
# SETUP
#

def setup(client):
    client.add_cog(Other(client))
