import sqlalchemy as sa

from discord.ext import commands, tasks
from common import config_h

#
# CLASSES
#

class Nexus(commands.Cog):
	def __init__(self, client):
		self.client = client
		#self.updates_table = sa.Table(
		#	'modupdates', client.db.meta,
		#	sa.Column('guild_id', sa.BigInteger, primary_key=True),
		#	sa.Column('channel_id', sa.BigInteger, primary_key=True),
		#	sa.Column('mod_id', sa.BigInteger, primary_key=True),
		#	sa.Column('game_domain', sa.String, primary_key=True),
		#	sa.Column('updated', sa.String, nullable=False),
		#	keep_existing=True
		#)

	def requirement_check(self):
		config = config_h.get()

		if not self.db.connected():
			return False

		if not "nexusApiToken" in config:
			return False

		return True

	async def cog_check(self, ctx):
		return ctx.channel.permissions_for(ctx.message.author).administrator

	@tasks.loop(hours=1.0)
	async def post_updates(self):
		pass

	@post_updates.before_loop
	async def before_post_updates(self):
		await self.client.wait_until_ready()

	#
	# COMMANDS
	#

	@commands.command()
	async def subscribe(self, ctx):
		pass

	@commands.command()
	async def unsubscribe(self, ctx):
		pass

#
# SETUP
#

def setup(client):
    client.add_cog(Nexus(client))