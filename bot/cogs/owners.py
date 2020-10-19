
"""
Much of the code is taken from: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py
"""
import subprocess
import sys

from discord.ext import commands, tasks
from common import config_h
from common.time_h import datetime_ext

#
#
#

MSG_LIMIT = 2000

#
# CLASSES
#

class Owners(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.outdated_reminder.start()

    @tasks.loop(hours=168.0)
    async def outdated_reminder(self):
        print("Checking for outdated components...")

        def blocking_process():
            cmd = [sys.executable, "-m", "pip", "list", "--outdated"]
            return subprocess.check_output(cmd, stderr = subprocess.STDOUT).decode(sys.stdout.encoding).strip()

        future = self.client.loop.run_in_executor(None, blocking_process)
        await future

        try:
            output = future.result()
            update_str = "--- {} ---\nUPDATE CHECK".format(datetime_ext.now())
            update_content = []

            while len(output) > 0:
                tmp_output = output[:MSG_LIMIT]
                output = output[len(tmp_output):]
                update_content.append("```{}```".format(tmp_output))

            for owner_id in self.client.owner_ids:
                user = await self.client.fetch_user(owner_id)
                dm = await user.create_dm()

                await dm.send(update_str)
                for part in update_content:
                    await dm.send(part) 

            output = update_content
            print("Finished the outdated component check...")

        except Exception as e:
            output = e.output

            print("Failed to check for outdated components:")

        finally:
            print(output)
        

    @outdated_reminder.before_loop
    async def before_reminder(self):
        await self.client.wait_until_ready()
        

    #
    # COMMANDS
    #

    async def cog_check(self, ctx):
       return ctx.author.id in self.client.owner_ids

    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        try:
            self.client.load_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        try:
            self.client.unload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    async def reload(self, ctx, *, module):
        try:
            self.client.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(
        name = 'refreshconf', 
        hidden = True)
    async def refresh_conf(self, ctx):
        conf = config_h.get(from_disk = True)

        self.client.command_prefix = conf['commandPrefix']
        self.client.owner_ids= conf['ownerIds']

        await ctx.send('\N{OK HAND SIGN}')

#
# SETUP
#

def setup(client):
    client.add_cog(Owners(client))