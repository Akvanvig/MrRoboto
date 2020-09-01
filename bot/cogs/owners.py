
"""
Much of the code is taken from: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py
"""

from discord.ext import commands
from common import config_h

#
# CLASSES
#

class Owners(commands.Cog):
    def __init__(self, client):
        self.client = client

    #
    # COMMANDS
    #

    async def cog_check(self, ctx):
       return ctx.author.id in self.client.owner_ids

    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        try:
            self.client.load_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        try:
            self.client.unload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    async def reload(self, ctx, *, module):
        try:
            self.client.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(
        name = 'refreshconf', 
        hidden = True)
    async def refresh_conf(self, ctx):
        conf = config_h.get(from_disk = True)

        self.client.command_prefix = conf['commandPrefix']
        self.client.owner_ids= conf['ownerIds']

        await ctx.send('\N{OK HAND SIGN}')

#
# SETUP
#

def setup(client):
    client.add_cog(Owners(client))