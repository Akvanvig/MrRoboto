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

    async def _unmute(self, member : Member):
        # Unmute on discord
        try:
            del self.muted_tasks[member]
        except KeyError:
            pass

        await member.remove_roles(utils.get(member.guild.roles, name = MUTED_ROLE))
            
        if member.voice: 
            await member.move_to(channel = member.voice.channel)

        # Delete mute from database
        await self._mute_delete(member)

    async def _mute(self, member : Member, mutetime : timedelta_ext):
        # Save mute to database
        await self._mute_save(member, mutetime)

        # Mute on discord
        await member.add_roles(utils.get(member.guild.roles, name = MUTED_ROLE))
        if member.voice: await member.move_to(channel = member.voice.channel)

        dm = await member.create_dm()
        await dm.send("You've been muted in {} for time period: {}".format(member.guild, str(mutetime)))

    async def _mute_save(self, member : Member, mutetime : timedelta_ext):
        async with self.client.db.acquire() as conn:
            unmutedate = str(mutetime.to_datetime_now())

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

    async def _mute_restore(self):
        async with self.client.db.acquire() as conn:
            currentdate = datetime_ext.now()

            async for row in conn.execute(self.muted_table.select()):
                guild = self.client.get_guild(row[self.muted_table.c.guild_id])
                member = guild.get_member(row[self.muted_table.c.user_id])
                unmutedate = datetime_ext.from_str(row[self.muted_table.c.unmutedate])

                # Unmute immediately
                if currentdate >= unmutedate:
                    asyncio.create_task(self._unmute(member))
                # Unmute later
                elif member not in self.muted_tasks:
                    task = Task(
                        loop = self.client.loop,
                        on_end = partial(self._unmute, member),
                        timedelta = (unmutedate - currentdate)
                    )
                    self.muted_tasks[member] = task
                    task.start()

    #
    # COMMANDS
    #

    async def cog_check(self, ctx):
        return ctx.channel.permissions_for(ctx.message.author).administrator

    @commands.command()
    async def mute(self, ctx, member : Member, mutetime : timedelta_ext):
        if mutetime <= DEFAULT_TIMEDELTA or mutetime > MUTETIME_LIMIT:
            raise commands.BadArgument("Specify a valid mute time between 0 and {}".format(str(MUTETIME_LIMIT)))

        try:
            task = self.muted_tasks[member]
            task.stop()
            await task.wait()
            
            task.timedelta = mutetime
            task.on_start = partial(self._mute_save, member, mutetime)
        except KeyError:
            task = Task(
                loop = self.client.loop,
                on_start = partial(self._mute, member, mutetime),
                on_end = partial(self._unmute, member),
                timedelta = mutetime
            )
            self.muted_tasks[member] = task
        finally:
            task.start()

    @commands.command()
    async def unmute(self, ctx, member : Member):
        try:
            self.muted_tasks[member].stop()
            del self.muted_tasks[member]
            await self._unmute(member)
        except KeyError:
            await ctx.send('User "{}" is not muted'.format(member.nick))

    @commands.command()
    async def sudo(self, ctx):
        await ctx.send("You are now running with sudo privileges")

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

    @_clear.command(
        name = 'all', 
        description = "Clears all chat messages in the channel, given a limit parameter.")
    async def _clear_all(self, ctx, lim = 30):
        if lim <= 0 or lim > HISTORY_LIMIT:
            await ctx.send("Choose a limit between 1 and {}".format(HISTORY_LIMIT))
        else:
            await ctx.channel.purge(limit = lim, before = ctx.message, bulk = True)

#
# SETUP
#

def setup(client):
    client.add_cog(Admin(client))

