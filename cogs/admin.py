import asyncio

from discord.ext import commands

#
# CLASSES
#

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Check if admin
    async def cog_check(self, ctx):
        return ctx.channel.permissions_for(ctx.message.author).administrator
        
    @commands.command()
    async def clear(self, ctx, *, lim=30):
        if lim <= 0 or lim > 300:
            await ctx.send("Choose a limit between 1 and 300")
        else:
            isCmdOrBot = lambda msg: True if msg.author == self.client.user or msg.content.startswith(self.client.command_prefix) else False
            await ctx.channel.purge(limit=lim, check=isCmdOrBot, before=ctx.message, bulk=True)

#
# SETUP
#

def setup(client):
    client.add_cog(Admin(client))