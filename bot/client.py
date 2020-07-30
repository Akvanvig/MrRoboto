#!/usr/bin/python3
"""
Simple discord bot.
Read: https://discordpy.readthedocs.io/en/latest/api.html
"""

__author__ = "Anders & Fredrico"

import os
import sys
import asyncio
import sqlalchemy as sa

from aiopg.sa import create_engine
from discord.ext import commands
from common.syncfunc import config_h
from psycopg2.errors import DuplicateTable

INITIAL_EXTENSIONS  = ['cogs.admin',
                       'cogs.animations',
                       'cogs.audio',
                       'cogs.commands',
                       'cogs.owners']

#
# CLASSES
#

# TODO(Fredrico/Anders): Config can be shared between classes

class PostgresDb:
    def __init__(self):
        # Private
        self._engine = None
        self._mock_engine = sa.create_engine('postgres://', strategy="mock", executor=self._mock_dump_sql)
        self._mock_dump = None
        self._started = asyncio.Event()
        
        # Public
        self.meta = sa.MetaData()
        self.exec_query = self._exec_query_wait

    def __del__(self):
        if self._engine: asyncio.run(self._engine.close())

    def _mock_dump_sql(self, sql, *multiparams, **params):
        self._mock_dump = str(sql.compile(dialect=self._mock_engine.dialect))

    # Execute query
    async def _exec_query(self, query):
        async with self._engine.acquire() as conn:
            result = await conn.execute(query)
            return await result.fetchall()

    # Wait for startup to finish
    async def _exec_query_wait(self, query):
        await self._started.wait()
        self._exec_query(query)

    # Startup the db
    async def startup(self):
        self._engine = await create_engine(**config_h.get()['postgresql'])

        # We can't call meta.create_all, as we're using
        # a mock_engine to get the sql query, meaning
        # the checkfirst arg is useless. As a result
        # create_all might throw a single DuplicateTable error
        # subsequently dropping to create new non-duplicate ones.
        # Therefore we create each table individually
        # and catch DuplicateTable errors on a per table basis.
        async with self._engine.acquire() as conn:
            for table in self.meta.tables.values():
                try:
                    table.create(bind=self._mock_engine)
                    await conn.execute(self._mock_dump)
                except DuplicateTable:
                    # Table already exist
                    pass

        self.exec_query = self._exec_query
        self._started.set()

class MrRoboto(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = PostgresDb()

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

        await self.db.startup()

    async def on_command(self, ctx):
        pass

    async def on_message(self, message):
        if message.author != client.user:
            print(message.author.name+": "+message.content)
        await client.process_commands(message)

    # Todo(Fredrico/Anders): Try to keep errors local
    # on a per command basis
    async def on_command_error(self, ctx, error):
        # Return if handled by local error handler
        if hasattr(ctx.command, "on_error"): return
        # Else
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("{}: {}".format(error.__class__.__name__, error))
        
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("Command \'{}\' not found".format(ctx.invoked_with))

        elif isinstance(error, commands.errors.CheckFailure):
            await ctx.send("{} is not allowed to run {} in {}. This incident will be reported".format(ctx.message.author, ctx.invoked_with, ctx.message.channel))

        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.send("Command \'{}\' is on cooldown for {:.2f} seconds".format(ctx.invoked_with, error.retry_after))

        else:
            print(error.__class__)
            await ctx.send("Command \'{}\' is not working properly, contact your local developer :)".format(ctx.invoked_with))
#
# MAIN
#

conf = config_h.get()

# Win32 compatibility for aiopg
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

client = MrRoboto(command_prefix = conf['commandPrefix'], case_insensitive = True, owner_ids = conf['ownerIds'])

for extension in INITIAL_EXTENSIONS:
    client.load_extension(extension)

client.run(conf['discordToken'], bot=True, reconnect=True)