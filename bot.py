"""Simple discord bot.
   Read: https://discordpy.readthedocs.io/en/latest/api.html
"""

__author__ = "Anders & Fredrico"

import os
import logging

from discord.ext.commands import Bot
from dotenv import load_dotenv

#
# STARTUP
#

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s: %(message)s"
)

if __name__ != '__main__':
    logging.critical("Script is not being run as standalone")
    quit()

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

#
# CONSTANTS
#

EXTENSIONS = ['cogs.animations',
              'cogs.commands']

TOKEN = os.getenv('DISCORD_TOKEN') # Example: fdjkakjdfefehsabh93,.3mejnfe
PREFIX = os.getenv('BOT_PREFIX') # Example: ?
OWNERS = os.getenv('BOT_OWNERS').split(',') # john,tesla,bob

if (TOKEN or PREFIX or OWNERS) == None:
    logging.critical("The .env file is missing a token")
    quit()

#
# CLASSES
#

class MrBot(Bot):
    async def on_ready(self):
        logging.info('Logged in as')
        logging.info(self.user.name)
        logging.info(self.user.id)
        logging.info('------')

    async def on_command(self, ctx):
        logging.info(ctx.message)

    async def on_disconnect(self):
        pass

#
# MAIN
#

bot = MrBot(command_prefix = PREFIX, case_insensitive = True, owner_ids = OWNERS)

for extension in EXTENSIONS:
    bot.load_extension(extension)

bot.run(TOKEN, bot=True, reconnect=True)