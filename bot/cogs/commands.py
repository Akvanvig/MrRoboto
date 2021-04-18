import asyncio
import random
import discord
import json

from discord.ext import commands
from common import config_h
from common.web_h import read_website_content

import urllib.request
import urllib.parse
import datetime  # This should use datetime_ext

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
        rate=1,
        per=30.0,
        type=commands.BucketType.member)
    async def kys(self, ctx):
        """don\'t"""
        async with ctx.typing():
            await asyncio.sleep(30)
            await ctx.send('What the fuck did you just fucking say about me, you little bitch? I’ll have you know I graduated top of my class in the Navy Seals, and I’ve been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I’m the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that’s just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little \'clever\' comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You’re fucking dead, kiddo.')

    @commands.command(
        name="remindme"
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
            {"title": "**Lead Project Manager** & **Service Manager**", "name": "**Adis Pinjic**"},
            {"title": "**Chief Technical Officer of the CTO's Department** & **Cuck**", "name": "**Eirik Habbestad**"},
            {"title": "**Chief Systems Architect** & **Qality Assurance Manager**", "name": "**Audun Solemdal**"},
            {"title": "**Chief Orkitect** & **Grand Master of the Memologists**", "name": "**Eirik 'El Lolando' Andersen**"},
            {"title": "**Chancellor of the Code** & **President of Marketing**", "name": "**Andreas 'Esteban' Hennestad**"},
            {"title": "**Head Officer of Security** & **Drug Dealer**", "name": "**Mikkel '天皇' Thoresen**"},
            {"title": "**Client Facing Human Resources Specialist** & **Code Harasser**", "name": "**Martina R. Førre**"},
            {"title": "code-monkeys", "name": "Anders & Fredrico"}
        ]

        len_title = len(max([i['title'] for i in users], key=len))
        len_name = len(max([i['name'] for i in users], key=len))

        fmt = '\n'.join(f"{_['title']:>{len_title}} -- {_['name']:{len_name}}" for _ in users)
        embed = discord.Embed(title='Credits', description=fmt)

        await ctx.send(embed=embed)

    @commands.command(
        name='weather'
    )
    async def weather(self, ctx, *, search: str):
        """Returns weather for given position"""

        lat = "59.9170"
        lon = "10.7274"
        config = config_h.get()

        # Get API-token
        if not "hereApiToken" in config:
            print("No Here API-token found, a new one can be created at developer.here.com")
            # raise exception
            return

        # Get coordinates
        # A Rest API Key from developer.here.com
        here_api_token = config["hereApiToken"]
        here_api_url = f"https://discover.search.hereapi.com/v1/discover?at={lat},{lon}&limit=1&q={urllib.parse.quote_plus(search)}&apiKey={here_api_token}"

        # Fetch data
        content = await read_website_content(self.client.loop, here_api_url)
        json_content = json.loads(content)

        result_coords = json_content["items"][0]["position"]
        result_loc = json_content["items"][0]["address"]

        # Fetch data
        search_request = urllib.request.Request(
            headers={"User-Agent": config['apiUserAgentIdentification']},
            url=f"https://api.met.no/weatherapi/locationforecast/2.0/compact.json?lat={round(result_coords['lat'],3)}&lon={round(result_coords['lng'],3)}"
        )

        content = await read_website_content(self.client.loop, search_request)
        json_content = json.loads(content)

        meta = json_content["properties"]["meta"]
        timeseries = json_content["properties"]["timeseries"]

        # Removing some unneeded data ¯\_(ツ)_/¯
        data = []

        for time in timeseries:
            # only checking temp midday cause I'm lazy and probably good enough, might implement properly some other time
            if time["time"].endswith("T12:00:00Z"):
                data.append(time)

        embed = discord.Embed(
            title=f"Weather Forecast for {result_loc['label']}")
        dateformat = "%Y-%m-%dT%H:%M:%fZ"

        # Adding to embeds
        for day in data:
            day_name = (datetime.datetime.strptime(
                day["time"], dateformat)).strftime("%A")
            extra_note = ""

            # Why not check windspeeds as well
            if day["data"]["instant"]["details"]["wind_speed"] > 32.6:
                extra_note = f"{day['data']['instant']['details']['wind_speed']} {meta['units']['wind_speed']} winds"

            # This should reaaaally not be so long - Fredrico
            embed.add_field(
                name=day_name, value=f"{day['data']['instant']['details']['air_temperature']} {meta['units']['air_temperature']}\n{day['data']['next_6_hours']['details']['precipitation_amount']} {meta['units']['precipitation_amount']}\n{day['data']['next_6_hours']['summary']['symbol_code']}  {extra_note}")

        # Sending :)
        await ctx.send(embed=embed)

#
# SETUP
#

def setup(client):
    client.add_cog(Other(client))
