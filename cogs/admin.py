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
        return commands.has_permissions(administrator=True)

    @commands.command()
    async def clear(self, ctx):
        history = ctx.channel.history(limit=10)
        msgs = [message async for message in history if message.author == self.client.user]
        
        for message in msgs:
            await message.delete()

#
# SETUP
#

def setup(client):
    client.add_cog(Admin(client))