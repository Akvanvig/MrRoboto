import asyncio

from discord.ext import commands

#
# CONSTANTS
#

HISTORY_LIMIT = 300

#
# CLASSES
#

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Check if admin
    async def cog_check(self, ctx):
        return ctx.channel.permissions_for(ctx.message.author).administrator
        
    @commands.group(name = 'clear', invoke_without_command = True, description = "Clears all bot commands and messages in the channel, given a limit parameter. Default is 30.")
    async def _clear(self, ctx, *, lim=30):
        if lim <= 0 or lim > HISTORY_LIMIT:
            await ctx.send("Choose a limit between 1 and {}".format(HISTORY_LIMIT))
        else:
            botuser = self.client.user
            prefix = self.client.command_prefix

            isCmdOrBot = lambda msg: True if msg.author == botuser or msg.content.startswith(prefix) else False
            
            await ctx.channel.purge(limit=lim, check=isCmdOrBot, before=ctx.message, bulk=True)

    @_clear.command(name = 'all', description = "Clears all chat messages in the channel, given a limit parameter. Default is 30.")
    async def _clear_all(self, ctx, *, lim=30):
        if lim <= 0 or lim > HISTORY_LIMIT:
            await ctx.send("Choose a limit between 1 and {}".format(HISTORY_LIMIT))
        else:
            await ctx.channel.purge(limit=lim, before=ctx.message, bulk=True)

#
# SETUP
#

def setup(client):
    client.add_cog(Admin(client))