#!/usr/bin/python3
"""
Simple discord bot.
Read: https://discordpy.readthedocs.io/en/latest/api.html
"""

__author__ = "Anders & Fredrico"

import os
import asyncio
import os.path as path

from discord import ClientException
from discord.ext import commands
from common import config_h, db_h

#
# CLASSES
#

class MrRoboto(commands.AutoShardedBot):
    def __init__(self):
        config = config_h.get()

        super().__init__(
            command_prefix=config['commandPrefix'],
            case_insensitive=True,
            owner_ids=config['ownerIds']
        )

        self.db = db_h.PostgresDB()

    def __load_extensions(self):
        cogs_dir = path.join(path.dirname(__file__), "cogs")
        extensions = []

        try:
            ignore = config_h.get()['ignoreExtensions']
        except KeyError:
            ignore = []

        for f in os.listdir(cogs_dir):
            name, ext = path.splitext(f)

            if ext != ".py" or name in ignore:
                continue

            extensions.append(f"cogs.{name}")

        for extension in extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(e)

    # Sneaky override
    def add_cog(self, cog):
        if not isinstance(cog, commands.Cog):
            raise TypeError('cogs must derive from Cog')

        cog_name = cog.__cog_name__
        existing = self._BotBase__cogs.get(cog_name)

        if existing is not None:
            if not override:
                raise ClientException(f'Cog named {cog_name!r} already loaded')
            self.remove_cog(cog_name)

        try:
            check = getattr(cog, 'requirement_check')
        except AttributeError:
            pass
        else:
            if not check():
                raise ClientException(f'Cog named {cog_name!r} did not fulfill the requirement check')

        cog = cog._inject(self)
        self._BotBase__cogs[cog_name] = cog

    async def start(self):
        config = config_h.get()

        await self.db.start(config['postgresql'])
        self.__load_extensions()
        await super().start(config['discordToken'], reconnect=True)

    async def close(self):
        await super().close()
        await self.db.stop()

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

def main():
    client = MrRoboto()
    client.run()

if __name__ == '__main__':
    main()
