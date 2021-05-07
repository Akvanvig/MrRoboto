import discord
import json
import urllib.request
import urllib.parse
import datetime  # This should use datetime_ext

from discord.ext import commands
from common import config_h, util_h

#
# CLASSES
#

class Weather(commands.Cog):
    def __init__(self, client):
        self.client = client

    #
    # COMMANDS
    #

    @commands.command(
        name='weather')
    async def weather(self, ctx, *, search: str):
        """Returns weather for given position"""

        lat = "59.9170"
        lon = "10.7274"
        config = config_h.get()

        # Get coordinates
        # A Rest API Key from developer.here.com
        here_api_token = config["hereApiToken"]
        here_api_url = f"https://discover.search.hereapi.com/v1/discover?at={lat},{lon}&limit=1&q={urllib.parse.quote_plus(search)}&apiKey={here_api_token}"

        # Fetch data
        content = await util_h.read_website_content(self.client.loop, here_api_url)
        json_content = json.loads(content)

        result_coords = json_content["items"][0]["position"]
        result_loc = json_content["items"][0]["address"]

        # Fetch data
        search_request = urllib.request.Request(
            headers={"User-Agent": config['apiUserAgentIdentification']},
            url=f"https://api.met.no/weatherapi/locationforecast/2.0/compact.json?lat={round(result_coords['lat'],3)}&lon={round(result_coords['lng'],3)}"
        )

        content = await util_h.read_website_content(self.client.loop, search_request)
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

def check(client):
    config = config_h.get()

    if not "hereApiToken" in config:
        print("No Here API-token found, a new one can be created at developer.here.com")
        return False

    return True

@util_h.requirement_check(check)
def setup(client):
    client.add_cog(Weather(client))