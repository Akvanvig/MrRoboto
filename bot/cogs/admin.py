import os
import asyncio
import sqlalchemy as sa

from discord import utils, Member
from discord.ext import commands
from common.time_h import DEFAULT_TIMEDELTA, datetime_ext, timedelta_ext, Task
from functools import partial

#
# CONSTANTS
#

MUTED_ROLE = "muted"
MUTETIME_LIMIT = timedelta_ext(days = 1)
HISTORY_LIMIT = 300

#
# CLASSES
#

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        
        self.muted_tasks = {}
        self.muted_table = sa.Table(
            'muted', client.db.meta,
            sa.Column('guild_id', sa.BigInteger, primary_key = True),
            sa.Column('user_id', sa.BigInteger, primary_key = True),
            sa.Column('unmutedate', sa.String, nullable = False),
            keep_existing = True
        )

    @commands.Cog.listener()
    async def on_ready(self):
        await self._mute_restore()

    # Check if admin
    async def cog_check(self, ctx):
        return ctx.channel.permissions_for(ctx.message.author).administrator

    # Sudo me' timbers
    @commands.command()
    async def sudo(self, ctx):
        await ctx.send("You are now running with sudo privileges")

    # Clear channel messages for bot and command messages
    @commands.group(
        name = 'clear', 
        invoke_without_command = True, 
        help = "Clears all bot commands and messages in the channel, given a limit parameter.")
    async def _clear(self, ctx, lim = 30):
        if lim <= 0 or lim > HISTORY_LIMIT:
            await ctx.send("Choose a limit between 1 and {}".format(HISTORY_LIMIT))
        else:
            botuser = self.client.user
            prefixes = tuple(self.client.command_prefix)

            def is_cmd_or_bot(msg):
                if msg.author == botuser or msg.content.startswith(prefixes): return True
                return False

            await ctx.channel.purge(limit=lim, check=is_cmd_or_bot, before=ctx.message, bulk=True)

    # Clear ALL channel messages
    @_clear.command(
        name = 'all', 
        description = "Clears all chat messages in the channel, given a limit parameter.")
    async def _clear_all(self, ctx, lim = 30):
        if lim <= 0 or lim > HISTORY_LIMIT:
            await ctx.send("Choose a limit between 1 and {}".format(HISTORY_LIMIT))
        else:
            await ctx.channel.purge(limit=lim, before=ctx.message, bulk=True)

    # Create save stmt for muted member
    def _mute_save_stmt(self, member : Member, mutetime : timedelta_ext):
        return self.muted_table.insert().values(
            guild_id = member.guild.id, 
            user_id = member.id, 
            unmutedate = mutetime.to_datetime_now().to_str()
        )

    # Create delete stmt for muted member
    def _mute_delete_stmt(self, member : Member):
        return self.muted_table.delete().where(
            sa.and_(
                self.muted_table.c.guild_id == member.guild.id, 
                self.muted_table.c.user_id == member.id
            )
        )

    # On_ready restore mutes
    async def _mute_restore(self):
        pass
        """async with self.client.db.acquire() as conn:
            currentdate = datetime_ext.now()
            member_tuples = []

            async for row in conn.execute(self.muted_table.select()):
                guild = self.client.get_guild(row[self.muted_table.c.guild_id])
                member = guild.get_member(row[self.muted_table.c.user_id])
                unmutedate = datetime_ext.from_str(row[self.muted_table.c.unmutedate])

                # Unmute immediately, and append to delete statement
                if currentdate >= unmutedate:
                    await self._unmute(member)
                    member_tuples.append((guild.id, member.id))
                # Unmute later
                elif member not in self.muted_tasks:
                    self.muted_tasks[member] = Task(
                        client = self.client,
                        coro = partial(self._unmute, member),
                        timedelta = (unmutedate - currentdate),
                        end_stmt = self._mute_delete_stmt(member)
                    )

            if len(member_tuples) > 0:
                await conn.execute(self.muted_table.delete().where(
                    sa.tuple_(
                        self.muted_table.c.guild_id, 
                        self.muted_table.c.user_id
                    ).in_(
                        member_tuples
                    )
                ))"""
    
    # Mute member for a given period of time
    @commands.command()
    async def mute(self, ctx, member : Member, mutetime : timedelta_ext):
        pass
        """if mutetime <= DEFAULT_TIMEDELTA or mutetime > MUTETIME_LIMIT:
            raise commands.BadArgument("Specify a valid mute time between 0 and {}".format(str(MUTETIME_LIMIT)))

        try:
            running_task = self.muted_tasks[member]
            running_task.stop()
            await running_task.wait()
            
            running_task.timedelta = mutetime
            running_task.start_stmt = self._mute_save_stmt(member, mutetime)
            running_task.start()
        except KeyError:
            self.muted_tasks[member] = Task(
                client = self.client,
                coro = partial(self._unmute, member),
                timedelta = mutetime,
                start_stmt = self._mute_save_stmt(member, mutetime),
                end_stmt = self._mute_delete_stmt(member)
            )

            await member.add_roles(utils.get(member.guild.roles, name = MUTED_ROLE))
            if member.voice: await member.move_to(channel = member.voice.channel)

            dm = await member.create_dm()
            await dm.send("You've been muted in {} for time period: {}".format(ctx.guild, str(mutetime)))"""

    async def _unmute(self, member : Member, *, stop_task = False):
        pass
        """
        try:
            if stop_task:
                self.muted_tasks[member].stop()

            del self.muted_tasks[member]

            await member.remove_roles(utils.get(member.guild.roles, name = MUTED_ROLE))
            
            if member.voice: 
                await member.move_to(channel = member.voice.channel)
        except KeyError:
            raise Exception('User "{}" is not muted'.format(member.nick))"""

    # Unmute member 
    @commands.command()
    async def unmute(self, ctx, member : Member):
        try:
            self.muted_tasks[member].stop()
            del self.muted_tasks[member]

            await self._unmute(member)
        except KeyError:
            await ctx.send('User "{}" is not muted'.format(member.nick))

#
# SETUP
#

def setup(client):
    client.add_cog(Admin(client))

