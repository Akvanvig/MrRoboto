
"""
Much of the code is taken from: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py
"""

import config

from discord.ext import commands

#
# CLASSES
#

class Owners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Check if owner
    async def cog_check(self, ctx):
       return ctx.author.id in self.bot.owner_ids

    # Load module
    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        try:
            self.bot.load_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    # Unload module
    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    # Reload module
    @commands.command(hidden=True)
    async def reload(self, ctx, *, module):
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    # Refresh config
    @commands.command(hidden=True)
    async def refreshconf(self, ctx):
        conf = config.getConf()

        self.bot.command_prefix = conf['commandPrefix']
        self.bot.owner_ids= conf['ownerIds']

        await ctx.send('\N{OK HAND SIGN}')

#
# SETUP
#

def setup(bot):
    bot.add_cog(Owners(bot))