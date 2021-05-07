import subprocess
import sys

from discord.ext import commands, tasks
from common import config_h, util_h, time_h

#
# CLASSES
#

class Owners(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.outdated_reminder.start()

    def cog_unload(self):
        self.outdated_reminder.cancel()

    async def cog_check(self, ctx):
        is_owner = await self.client.is_owner(ctx.author)
        return is_owner

    @tasks.loop(hours=168.0)
    async def outdated_reminder(self):
        print("Checking for outdated components...")

        try:
            output = await self.client.loop.run_in_executor(None, self._get_pip_outdated)

            update_str = f"--- {time_h.datetime_ext.now()} ---\nUPDATE CHECK"
            update_content = util_h.message_split(output, length=1950)
            messages = []

            for i in range(len(update_content)):
                if i == 0:
                    if not update_content[0]:
                        messages.append(f"{update_str}\nNo outdated packages")
                    else:
                        messages.append(f"{update_str}\n```{update_content[0]}```")
                else:
                    messages.append(f"```{update_content[i]}```")

            if not self.client.owner_ids:
                app = await self.client.application_info()
                self.client.owner_ids = ids = {m.id for m in app.team.members}

            for owner_id in self.client.owner_ids:
                user = await self.client.fetch_user(owner_id)
                dm = await user.create_dm()
                for message_part in messages:
                    await dm.send(message_part)

            print(update_content)
            print("Finished the outdated component check...")

        except subprocess.CalledProcessError as e:
            print(e.output)
            print("Process error, Failed to check for outdated components...")

        except Exception:
            print("Fatal error, Failed to check for outdated components...")

    @outdated_reminder.before_loop
    async def before_reminder(self):
        await self.client.wait_until_ready()

    def _get_pip_outdated(self):
        cmd = [sys.executable, "-m", "pip", "list", "--outdated"]
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode(sys.stdout.encoding).strip()

    #
    # COMMANDS
    #

    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        try:
            self.client.load_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        try:
            self.client.unload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.command(hidden=True)
    async def reload(self, ctx, *, module):
        try:
            self.client.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")
        else:
            await ctx.send("\N{OK HAND SIGN}")

#
# SETUP
#

def setup(client):
    client.add_cog(Owners(client))
