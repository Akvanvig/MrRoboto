import asyncio
import random
import discord

from discord.ext import commands

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

#
# CLASSES
#

class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    #
    # COMMANDS
    #

    @commands.command(
        name='latency'
    )
    async def latency(self, ctx):
        """Returns latency between the bot and the Discord servers"""
        await ctx.send(f"Bot latency is {self.client.latency:.2f} ms")

    @commands.command(
        name='choose'
    )
    async def choose(self, ctx):
        """Picks a random alternative from given space separated options"""
        choices = ctx.message.clean_content.split(" ")
        if len(choices) <= 1:
            raise commands.UserInputError("Must specify choices")
        await ctx.send(f"'{random.choice(choices)}' has been chosen")


    @commands.command(
        name='kys'
    )
    @commands.cooldown(
        rate = 1,
        per = 30.0,
        type = commands.BucketType.member)
    async def kys(self, ctx):
        """don\'t"""
        async with ctx.typing():
            await asyncio.sleep(30)
            await ctx.send('What the fuck did you just fucking say about me, you little bitch? I’ll have you know I graduated top of my class in the Navy Seals, and I’ve been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I’m the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that’s just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little \'clever\' comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You’re fucking dead, kiddo.')

    @commands.command(
        name = "remindme"
    )
    async def remind_me(self, ctx, *time):
        """Set up a reminder in given amount of time"""
        pass

    @commands.command(
        name='credits'
    )
    async def credits(self, ctx):
        """Show development team behind this magnificent bot"""
        users = [
            {"title":"**Lead Project Manager**, **Service Manager**", "name":"**Adis Pinjic**"},
            {"title":"**Chief Systems Architect** & **Qality Assurance Manager**", "name":"**Audun Solemdal**"},
            {"title":"**Chief Orkitect** & **Grand Master of the Memologists**", "name":"**Eirik 'El Lolando' Andersen**"},
            {"title":"**Chancellor of the Code** & **President of Marketing**", "name":"**Andreas 'Esteban' Hennestad**"},
            {"title":"**Head Officer of Security** & **Drug Dealer**", "name":"**Mikkel '天皇' Thoresen**"},
            {"title":"**Client Facing Human Resources Specialist** & **Code Harasser**", "name": "**Martina R. Førre**"},
            {"title":"code-monkeys", "name":"Anders & Fredrico"}
        ]
        lenTitle = len(max([i['title'] for i in users], key=len))
        lenName = len(max([i['name'] for i in users], key=len))
        fmt = '\n'.join(f"{_['title']:>{lenTitle}} -- {_['name']:{lenName}}" for _ in users)
        embed = discord.Embed(title='Credits', description=fmt)

        await ctx.send(embed=embed)

    @commands.command(
        name = "rule34"
    )
    @commands.is_nsfw() #Only works if in nsfw channel
    async def rule_thirtyfour(self, ctx, *, search: str):
        """Search for rule34 images
        Will only work in nsfw channels
        ------------
        search: string searchterm, separate keywords using space or *
        """
        search = search.replace(' ', '*')
        searchUrl = f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags={urllib.parse.quote_plus(search)}"

        #Feching data
        webpage = urllib.request.urlopen(searchUrl)

        #Fetching response from xml
        tree = ET.fromstring(webpage.read())
        if len(tree):
            imageUrl = tree[random.randrange(len(tree))].get('file_url')
            await ctx.send(imageUrl)
        else:
            await ctx.send(f"No results found for {search}")



#
# SETUP
#

def setup(client):
    client.add_cog(Other(client))
