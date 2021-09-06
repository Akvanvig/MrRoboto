import asyncio
import random
import discord
import os.path

from discord.ext import commands
from common import config_h

#
# CLASSES
#

class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    #
    # COMMANDS
    #

    @commands.command(
        name='latency')
    async def latency(self, ctx):
        """Returns latency between the bot and the Discord servers"""
        await ctx.send(f"Bot latency is {self.client.latency:.2f} ms")

    @commands.command(
        name='choose')
    async def choose(self, ctx):
        """Picks a random alternative from given space separated options"""
        choices = ctx.message.clean_content.split(" ")
        if len(choices) <= 1:
            raise commands.UserInputError("Must specify choices")
        await ctx.send(f"'{random.choice(choices)}' has been chosen")

    @commands.command(
        name='kys')
    @commands.cooldown(
        rate=1,
        per=30.0,
        type=commands.BucketType.member)
    async def kys(self, ctx):
        """don\'t"""
        async with ctx.typing():
            await asyncio.sleep(30)
            await ctx.send('What the fuck did you just fucking say about me, you little bitch? I’ll have you know I graduated top of my class in the Navy Seals, and I’ve been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I’m the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that’s just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little \'clever\' comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You’re fucking dead, kiddo.')

    @commands.command(
        name="remindme")
    async def remind_me(self, ctx, *time):
        """Set up a reminder in given amount of time"""
        pass

    @commands.command(
        name='credits')
    async def credits(self, ctx):
        """Show development team behind this magnificent bot"""
        desc = (
            "**Lead Project Manager** & **Service Manager** -- **Adis Pinjic**\n"
            "**Chief Technical Officer of the CTO's Department** & **Cuck** -- **Eirik Habbestad**\n"
            "**Chief Systems Architect** & **Qality Assurance Manager** -- **Audun Solemdal**\n"
            "**Chief Orkitect**, **hr**, & **Grand Master of the Memologists** -- **Eirik 'El Lolando' Andersen**\n"
            "**Chancellor of the Code** & **President of Marketing** -- **Andreas 'Esteban' Hennestad**\n"
            "**Head Officer of Security** & **Drug Dealer** -- **Mikkel '天皇' Thoresen**\n"
            "**Client Facing Human Resources Specialist** & **Code Harasser** -- **Martina R. Førre**\n"
            "**Investor** & **Mainframe DevOps Hacker** -- **Bendiks R. Øverbø**\n"
            "**Cloud Enginør** & **Reitan Group Representative** -- **Magnar Reitan**\n"
            "code-monkeys -- Anders & Fredrico"
        )

        embed = discord.Embed(title='Credits', description=desc)
        await ctx.send(embed=embed)

    @commands.command(
        name='catjam')
    async def catjam(self, ctx):
        """Returns catjam"""
        gif_path = os.path.join(config_h.MEDIA_DIR, 'gifs/catjam.gif')
        pic_file = discord.File(gif_path)
        await ctx.send(file=pic_file)
#
# SETUP
#

def setup(client):
    client.add_cog(Other(client))
