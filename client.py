"""
Simple discord bot.
Read: https://discordpy.readthedocs.io/en/latest/api.html
"""

__author__ = "Anders & Fredrico"

import logging
import config

from discord.ext import commands

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s: %(levelname)s: %(message)s"
)

initial_extensions  = ['cogs.animations',
                       'cogs.audio',
                       'cogs.commands',
                       'cogs.owners']

#
# CLASSES
#

class MrRoboto(commands.Bot):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_command(self, ctx):
        logging.info(ctx.author.name+": "+ctx.message.content)

    async def on_message(self, message):
        if message.author != client.user:
            print(message.content)
        await client.process_commands(message)


    async def on_command_error(self, ctx, error):
        if error.__class__ is commands.MissingRequiredArgument:
            await ctx.send('{}: {}'.format(error.__class__.__name__, error))
        elif error.__class__ is commands.CommandNotFound:
            await ctx.send('command \'{}\' not found'.format(ctx.invoked_with))
        else:
            print(error)
            await ctx.send('command \'{}\' is not working properly, contact your local developer :)'.format(ctx.invoked_with))
#
# MAIN
#

conf = config.get()

client = MrRoboto(command_prefix = conf['commandPrefix'], case_insensitive = True, owner_ids = conf['ownerIds'])

for extension in initial_extensions:
    client.load_extension(extension)

client.run(conf['discordToken'], bot=True, reconnect=True)
