"""
Simple discord bot.
Read: https://discordpy.readthedocs.io/en/latest/api.html
"""

__author__ = "Anders & Fredrico"

import os
import logging

from discord.ext import commands
from dotenv import load_dotenv

#
# STARTUP
#

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s: %(levelname)s: %(message)s"
)

if os.path.exists("./.env") == False:
    logging.warning("The .env file is missing, creating a new one")
    
    with open('./.env', 'a') as file:
        file.write("# .env\n")
        file.write("DISCORD_TOKEN=\n\n")
        file.write("BOT_PREFIX=\n")
        file.write("BOT_OWNERS=")

    logging.critical("Fill the required fields in the .env file and run the script again")
    quit()

load_dotenv()

initial_extensions  = ['cogs.admin',
                       'cogs.animations',
                       'cogs.commands']

TOKEN = os.getenv('DISCORD_TOKEN') # Example: fdjkakjdfefehsabh93,.3mejnfe
PREFIX = os.getenv('BOT_PREFIX') # Example: ?
OWNERS = set(map(int, os.getenv('BOT_OWNERS').split(','))) # 321314124,52635,22342135423

if (TOKEN or PREFIX or OWNERS) == None:
    logging.critical("The .env file is missing a token")
    quit()

#
# CLASSES
#

class MrBot(commands.Bot):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_command(self, ctx):
        logging.info(ctx.author.name+": "+ctx.message.content)

    async def on_command_error(self, ctx, error):
        if error.__class__ == commands.MissingRequiredArgument:
            await ctx.send(f'{error.__class__.__name__}: {error}')

#
# MAIN
#

bot = MrBot(command_prefix = PREFIX, case_insensitive = True, owner_ids = OWNERS)

for extension in initial_extensions:
    bot.load_extension(extension)

bot.run(TOKEN, bot=True, reconnect=True)