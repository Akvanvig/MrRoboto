import os
import asyncio

from discord.ext import commands
from common import *

#
# CONSTANTS
#

MUTED_PATH = "./state/muted.json"
HISTORY_LIMIT = 300
MUTETIME_LIMIT = timehelper.args_to_delta(days = 1)

#
# CLASSES
#

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Check mute list if we're booting up
    # to avoid permanent mutes
    @staticmethod
    async def ready(client):
        if not os.path.isfile(MUTED_PATH):
            jsonhelper.saveJson({}, MUTED_PATH)
            return

        currentdate = timehelper.get_current_date()
        json = jsonhelper.getJson(MUTED_PATH)
        
        members_to_unmute = []

        for guild_id, members in json.items():
            guild = client.get_guild(int(guild_id))

            for member_id, date in members.items():
                member = guild.get_member(int(member_id))
                mutedate = timehelper.str_to_date(date)

                if currentdate >= mutedate:
                    members_to_unmute.append(member)
                else:
                    unmuteseconds = (mutedate - currentdate).total_seconds()
                    asyncio.create_task(asynchelper.run_coro_in(Admin._unmute(member), unmuteseconds))

        if len(members_to_unmute) > 0:
            await Admin._unmute(*members_to_unmute)

    # Unmute member(s) and remove them from the json list
    @staticmethod
    async def _unmute(*members):
        json = jsonhelper.getJson(MUTED_PATH)
        
        for member in members:
            try:
                del json[str(member.guild.id)][str(member.id)]
            except KeyError as e:
                pass # Do nothing

        jsonhelper.saveJson(json, MUTED_PATH)
        
        for member in members:
            await member.edit(mute = False)

    # Check if admin
    async def cog_check(self, ctx):
        return ctx.channel.permissions_for(ctx.message.author).administrator

    # Sudo me' timbers
    @commands.command()
    async def sudo(self, ctx):
        await ctx.send("You are now running with sudo privileges")

    # Clear channel messages for bot and command messages
    @commands.group(name = 'clear', invoke_without_command = True, help = "Clears all bot commands and messages in the channel, given a limit parameter. Default is 30.")
    async def _clear(self, ctx, lim = 30):
        if lim <= 0 or lim > HISTORY_LIMIT:
            await ctx.send("Choose a limit between 1 and {}".format(HISTORY_LIMIT))
        else:
            botuser = self.client.user
            prefixes = tuple(self.client.command_prefix)

            isCmdOrBot = lambda msg: True if msg.author == botuser or msg.content.startswith(prefixes) else False

            await ctx.channel.purge(limit=lim, check=isCmdOrBot, before=ctx.message, bulk=True)

    # Clear ALL channel messages
    @_clear.command(name = 'all', description = "Clears all chat messages in the channel, given a limit parameter. Default is 30.")
    async def _clear_all(self, ctx, lim = 30):
        if lim <= 0 or lim > HISTORY_LIMIT:
            await ctx.send("Choose a limit between 1 and {}".format(HISTORY_LIMIT))
        else:
            await ctx.channel.purge(limit=lim, before=ctx.message, bulk=True)

    @commands.command()
    async def mute(self, ctx, name, *time):
        member = ctx.guild.get_member_named(name)

        if member == None:
            await ctx.send("Could not find any user named {}".format(name))
            return

        mutetime = timehelper.str_to_delta("".join(time))

        if mutetime <= timehelper.DEFAULT_TIMEDELTA or mutetime > MUTETIME_LIMIT:
            await ctx.send("Specify a valid mute time between 0 and {}".format(str(MUTETIME_LIMIT)))
            return

        unmutedate = timehelper.date_to_str(timehelper.get_current_date() + mutetime)

        json = jsonhelper.getJson(MUTED_PATH)
        json.setdefault(str(ctx.guild.id), {})[str(member.id)] = unmutedate
        jsonhelper.saveJson(json, MUTED_PATH)

        await member.edit(mute = True)
        await asyncio.sleep(mutetime.total_seconds())
        await Admin._unmute(member)

#
# SETUP
#

def setup(client):
    client.add_cog(Admin(client))

