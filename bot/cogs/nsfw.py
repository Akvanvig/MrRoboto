import urllib.parse
import xml.etree.ElementTree as ET
import random

from discord.ext import commands
from common import util_h

#
# CLASSES
#

class Nsfw(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        return ctx.channel.is_nsfw()

    #
    # COMMANDS
    #

    @commands.command(name="rule34")
    async def rule_thirtyfour(self, ctx, *, search: str):
        """Search for rule34 images Will only work in nsfw channels
        ------------
        search: string searchterm, separate keywords using space or *
        """

        search = search.replace(" ", "*")
        url = f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags={urllib.parse.quote_plus(search)}"

        # Fetching data
        tree = await util_h.read_website_content(url, ET)

        if not len(tree):
            await ctx.send(f"No results found for {search}")
        else:
            img_url = tree[random.randrange(len(tree))].get("file_url")
            await ctx.send(img_url)

#
# SETUP
#

def setup(client):
    client.add_cog(Nsfw(client))