#!/usr/bin/python3
"""
Simple discord bot.
Read: https://discordpy.readthedocs.io/en/latest/api.html
"""

__author__ = "Anders & Fredrico"

import os
import sys
import asyncio

from discord.ext import commands
from common import config_h
from common.db_h import PostgresDB

Extensions = [
    'cogs.admin',
    'cogs.animations',
    'cogs.audio',
    'cogs.commands',
    'cogs.nsfw',
    'cogs.owners'
]

#
# CLASSES
#

class MrRoboto(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = PostgresDB()

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("------")

    async def on_command(self, ctx):
        pass

    async def on_message(self, message):
        if message.author != self.user:
            print(message.author.name+": "+message.content)
        await self.process_commands(message)

    # TODO(Fredrico/Anders): Try to keep errors local on a per command basis
    async def on_command_error(self, ctx, error):
        # Return if handled by local error handler
        if hasattr(ctx.command, "on_error"):
            return

        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if issubclass(type(error), commands.UserInputError):
            await ctx.send(f"{error.__class__.__name__}: {error}")

        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Command '{ctx.invoked_with}' not found")

        elif isinstance(error, commands.errors.CheckFailure):
            await ctx.send(f"{ctx.message.author} is not allowed to run {ctx.invoked_with} in {ctx.message.channel}. This incident will be reported")

        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.send(f"Command '{ctx.invoked_with}' is on cooldown for {error.retry_after:.2f} seconds")

        else:
            print(error.__class__)
            print(error)
            await ctx.send(f"Command '{ctx.invoked_with}' is not working properly, contact your local developer :)")
#
# MAIN
#

async def start(client: MrRoboto, conf):
    await client.db.start(conf['postgresql'])
    await client.start(conf['discordToken'], bot=True, reconnect=True)

async def stop(client: MrRoboto):
    await client.close()
    await client.db.stop()

def main():
    loop = asyncio.get_event_loop()
    conf = config_h.get()

    client = MrRoboto(
        loop=loop,
        command_prefix=conf['commandPrefix'],
        case_insensitive=True,
        owner_ids=conf['ownerIds']
    )

    for extension in Extensions:
        client.load_extension(extension)

    try:
        loop.run_until_complete(start(client, conf))
    except KeyboardInterrupt:
        loop.run_until_complete(stop(client))
    finally:
        loop.close()

if __name__ == '__main__':
    main()
