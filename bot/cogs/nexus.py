import sqlalchemy as sa
import asyncio
import json
import discord
import urllib.request

from discord.ext import commands, tasks
from common import config_h, web_h

class ChannelError(Exception):
	def __init__(self, msg = ""):
		super().__init__(msg)

class ModError(Exception):
	def __init__(self, msg = ""):
		super().__init__(msg)

#
# CLASSES
#

class Nexus(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.lock = asyncio.Lock()
		self.nexus_url = "www.nexusmods.com/"
		self.api_url = "api.nexusmods.com/v1/"

		self.update_table = sa.Table(
			'modupdates', client.db.meta,
			sa.Column('channel_id', sa.BigInteger, primary_key=True),
			sa.Column('game_domain', sa.String, primary_key=True),
			sa.Column('mod_id', sa.BigInteger, primary_key=True),
			sa.Column('updated', sa.String, nullable=False),
			keep_existing=True
		)

		self.post_updates.start()

	def cog_unload(self):
		self.post_updates.cancel()

	def requirement_check(self):
		config = config_h.get()

		if not self.client.db.exists():
			return False

		if not "nexusApiToken" in config:
			return False

		return True

	async def cog_check(self, ctx):
		return ctx.channel.permissions_for(ctx.message.author).administrator

	@tasks.loop(hours=1.0)
	async def post_updates(self):
		config = config_h.get()
		header = {
			"apiKey": config["nexusApiToken"],
			"User-Agent": config['apiUserAgentIdentification']
		}

		async with self.lock:
			async with self.client.db.begin() as conn:
				result = await conn.stream(self.update_table.select())
				prune, updated = await self._check_for_updates(header, result)

				await self._prune(conn, prune)
				await self._update(conn, updated)

	@post_updates.before_loop
	async def before_post_updates(self):
		await self.client.wait_until_ready()

	async def _check_for_updates(self, header, result):
		prune = []
		updated = []

		async for row in result:
			try:
				timestamp = await self._post_if_updated(
					header,
					row["channel_id"],
					row["game_domain"],
					row["mod_id"],
					row["updated"]
				)

				if not timestamp:
					continue
			except ChannelError as e:
				table_key = sa.and_(
					"channel_id" == row["channel_id"],
					"game_domain" == row["game_domain"],
					"mod_id" == row["mod_id"]
				)
				prune.append(table_key)
			else:
				table_key = sa.and_(
					"channel_id" == row["channel_id"],
					"game_domain" == row["game_domain"],
					"mod_id" == row["mod_id"]
				)
				updated.append((timestamp, table_key))

		return prune, updated

	async def _post_if_updated(self, api_header, channel_id, game, mod, old_date):
		request = urllib.request.Request(
			headers=header,
			url=f"{self.api_url}games/{game}/mods/{mod}.json"
		)

		mod_response = await read_website_content(self.client.loop, request)
		mod_response = json.loads(mod_response)
		new_date = mod_response["updated_timestamp"]

		if new_date <= old_date:
			return None

		request = urllib.request.Request(
			headers=header,
			url=f"{self.api_url}games/{game}/mods/{mod}/changelogs.json"
		)

		mod_changelog_response = await read_website_content(self.client.loop, request)
		mod_changelog_response = json.loads(mod_changelog_response)
		channel = await self.client.fetch_channel(channel_id)

		if not channel:
			raise ChannelError()

		message = discord.Embed(
			title=f"Update: {mod_response['name']}",
			url=f"{self.nexus_url}{game}/mods/{mod}",
			description=mod_response["summary"]
		)
		message.set_author(name=mod_response["uploaded_by"], url=f"{self.nexus_url}users/{mod_response['user']['member_id']}")
		message.set_image(url=mod_response["picture_url"])
		message.set_footer(text=f"Was updated at {mod_response['updated_time']}")

		await channel.send(embed=message)

		return new_date

	async def _prune(self, conn, prune):
		for to_delete in prune:
			await conn.execute(self.update_table.delete().where(
				to_delete
			))

	async def _update(self, conn, updated):
		for timestamp, to_update in updated:
			await conn.execute(self.update_table.update().values(
				updated=timestamp).\
			where(
				to_update
			))

	#
	# COMMANDS
	#

	@commands.command(
		name="subscribetomod")
	async def subscribe_mod(self, ctx, channel : discord.TextChannel, game : str, mod : int):
		if not channel:
			raise ChannelError()

		if ctx.guild != channel.guild:
			raise ChannelError()

		config = config_h.get()
		request = urllib.request.Request(
			headers={
				"apiKey": config["nexusApiToken"],
				"User-Agent": config['apiUserAgentIdentification']
			},
			url=f"{self.api_url}games/{game}/mods/{mod}/changelogs.json"
		)

		response = await read_website_content(self.client.loop, request)

		if response.status_code == 404:
			raise ModError()

		response = json.loads(response)

		async with self.lock:
			async with self.client.db.begin() as conn:
				await conn.execute(self.update_table.insert().values(
					channel_id=channel.id,
					game_domain=game,
					mod_id=mod,
					updated=response["updated_timestamp"]
				))

		await ctx.send("TEST")

	@commands.command(
		name="unsubscribefrommod")
	async def unsubscribe_mod(self, ctx, channel : discord.TextChannel, game : str, mod : int):
		if not channel:
			raise ChannelError()

		if ctx.guild != channel.guild:
			raise ChannelError()

		async with self.lock:
			async with self.client.db.begin() as conn:
				await conn.execute(self.update_table.delete().where(
					sa.and_(
						"channel_id" == channel.id,
						"game_domain" == game,
						"mod_id" == mod
					)
				))

		await ctx.send("TEST")

	#
	# ERRORS
	#

	@subscribe_mod.error
	@unsubscribe_mod.error
	async def subscription_error(self, ctx, error):
		pass

#
# SETUP
#

def setup(client):
    client.add_cog(Nexus(client))