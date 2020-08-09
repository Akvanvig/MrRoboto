import os
import asyncio
import sqlalchemy as sa

from discord import utils, Member
from discord.ext import commands
from common.asyncfunc import async_h
from common.syncfunc.time_h import DEFAULT_TIMEDELTA, datetime_ext, timedelta_ext, Task
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
        self.muted_members = {}

        self.muted_table = sa.Table(
            'muted', client.db.meta,
            sa.Column('guild_id', sa.BigInteger, primary_key = True),
            sa.Column('user_id', sa.BigInteger, primary_key = True),
            sa.Column('unmutedate', sa.String, nullable = False),
            keep_existing = True
        )

    @commands.Cog.listener()
    async def on_ready(self):
        # Read mute list from disk on_ready to avoid permanent mutes
        async with self.client.db.acquire() as conn:
            currentdate = datetime_ext.now()
            members_tuple = []

            async for row in conn.execute(self.muted_table.select()):
                guild = self.client.get_guild(row[self.muted_table.c.guild_id])
                member = guild.get_member(row[self.muted_table.c.user_id])
                unmutedate = datetime_ext.from_str(row[self.muted_table.c.unmutedate])

                # Unmute immediately, and append to delete statement
                if currentdate >= unmutedate:
                    await self._unmute(member)
                    members_tuple.append((guild.id, member.id))
                # Unmute later
                elif member not in self.muted_members:
                    mute_task = Task(
                        coro = partial(self._unmute, member),
                        count = 1,
                        delay = True,
                        seconds = (unmutedate - currentdate).total_seconds()
                    )
                    self.muted_members[member] = mute_task

                    mute_task.after_loop(partial(self._mute_delete, member))
                    mute_task.start()

            if len(members_tuple) > 0:
                await conn.execute(self.muted_table.delete().where(
                    sa.tuple_(
                        self.muted_table.c.guild_id, self.muted_table.c.user_id
                    ).in_(
                        members_tuple
                    )
                ))

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

    # Unmute member and remove them from the json list
    async def _unmute(self, member : Member):
        try:
            del self.muted_members[member]
        except KeyError:
            pass

        await member.remove_roles(utils.get(member.guild.roles, name = MUTED_ROLE))
        if member.voice: await member.move_to(channel = member.voice.channel)

    # Unmute member 
    @commands.command()
    async def unmute(self, ctx, member : Member):
        if member in self.muted_members:
            await self._unmute(member)
        else:
            # Raise error, user is not muted
            pass


    async def _mute_save(self, member : Member, mutetime : timedelta_ext):
        async with self.client.db.acquire() as conn:
            unmutedate = mutetime.to_datetime_now().to_str()

            await conn.execute(sa.dialects.postgresql.insert(self.muted_table).values(
                guild_id = member.guild.id, 
                user_id = member.id, 
                unmutedate = unmutedate
                ).on_conflict_do_update(
                constraint = self.muted_table.primary_key,
                set_ = dict(unmutedate = unmutedate)
            ))

    async def _mute_delete(self, member : Member):
        async with self.client.db.acquire() as conn:
            await conn.execute(self.muted_table.delete().where(
                sa.and_(
                    self.muted_table.c.guild_id == member.guild.id, 
                    self.muted_table.c.user_id == member.id
                )
            ))
    
    # Mute member for a given period of time
    @commands.command()
    async def mute(self, ctx, member : Member, mutetime : timedelta_ext):
        if mutetime <= DEFAULT_TIMEDELTA or mutetime > MUTETIME_LIMIT:
            raise commands.BadArgument("Specify a valid mute time between 0 and {}".format(str(MUTETIME_LIMIT)))

        try:
            running_task = self.muted_members[member]
            running_task.stop()

            running_task.change_interval(seconds = mutetime.total_seconds())
            running_task.before_loop(partial(self._mute_save, member, mutetime))
            running_task.start()
        except KeyError:
            mute_task = Task(
                coro = partial(self._unmute, member), 
                count = 1, 
                delay = True,
                seconds = mutetime.total_seconds()
            )
            self.muted_members[member] = mute_task

            mute_task.before_loop(partial(self._mute_save, member, mutetime))
            mute_task.after_loop(partial(self._mute_delete, member))
            mute_task.start()

            await member.add_roles(utils.get(member.guild.roles, name = MUTED_ROLE))
            if member.voice: await member.move_to(channel = member.voice.channel)

            dm = await member.create_dm()
            await dm.send("You've been muted in {} for time period: {}".format(ctx.guild, str(mutetime)))

#
# SETUP
#

def setup(client):
    client.add_cog(Admin(client))

