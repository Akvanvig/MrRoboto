#!/usr/bin/python3
"""
Simple discord bot.
Read: https://discordpy.readthedocs.io/en/latest/api.html
"""

__author__ = "Anders & Fredrico"

import os
import sys
import logging
import asyncio

from discord.ext import commands
from common.asyncfunc import db_h
from common.syncfunc import config_h

INITIAL_EXTENSIONS  = ['cogs.admin',
                       'cogs.animations',
                       'cogs.audio',
                       'cogs.commands',
                       'cogs.owners']

#
# CLASSES
#

class MrRoboto(commands.Bot):
    def __init__(self):
        super().__init__()
        self.db = db_h.Db()

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

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