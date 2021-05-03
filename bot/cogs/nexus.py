import sqlalchemy as sa
import asyncio
import json
import discord
import urllib.request

from discord.ext import commands, tasks
from common import config_h, web_h, util_h


class HttpError(Exception):
    def __init__(self, msg = ""):
        super().__init__(msg)

class ChannelError(commands.CommandError):
    pass

class ModError(commands.CommandError):
    pass

#
# CLASSES
#

class Nexus(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.lock = asyncio.Lock()
        self.nexus_url = "https://www.nexusmods.com/"
        self.api_url = "https://api.nexusmods.com/v1/"

        self.update_table = sa.Table(
            'modupdates', client.db.meta,
            sa.Column('channel_id', sa.BigInteger, primary_key=True),
            sa.Column('game_domain', sa.String, primary_key=True),
            sa.Column('mod_id', sa.BigInteger, primary_key=True),
            sa.Column('updated', sa.BigInteger, nullable=False),
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
                    self.update_table.c.channel_id == row["channel_id"],
                    self.update_table.c.game_domain == row["game_domain"],
                    self.update_table.c.mod_id == row["mod_id"]
                )
                prune.append(table_key)
            else:
                table_key = sa.and_(
                    self.update_table.c.channel_id == row["channel_id"],
                    self.update_table.c.game_domain == row["game_domain"],
                    self.update_table.c.mod_id == row["mod_id"]
                )
                updated.append((timestamp, table_key))

        return prune, updated

    async def _post_if_updated(self, header, channel_id, game, mod, old_date):
        request = urllib.request.Request(
            headers=header,
            url=f"{self.api_url}games/{game}/mods/{mod}.json"
        )

        mod_response = await web_h.read_website_content(self.client.loop, request)
        mod_response = json.loads(mod_response)
        new_date = mod_response["updated_timestamp"]

        if new_date <= old_date:
            return None

        request = urllib.request.Request(
            headers=header,
            url=f"{self.api_url}games/{game}/mods/{mod}/changelogs.json"
        )

        mod_changelog_response = await web_h.read_website_content(self.client.loop, request)
        mod_changelog_response = json.loads(mod_changelog_response)
        channel = await self.client.fetch_channel(channel_id)

        if not channel:
            raise ChannelError("Channel has been deleted")

        changelog_versions = list(mod_changelog_response.keys())
        changelog = ""

        if changelog_versions:
            version = changelog_versions[-1]
            changelog_l = mod_changelog_response[version]

            if len(changelog_l) > 5:
                changelog_l = changelog_l[:5]

            changelog_l = '\n'.join(changelog_l)
            changelog = f"Latest changelog [{version}]:\n{changelog_l}\n..."

        message = discord.Embed(
            title=mod_response["name"],
            url=f"{self.nexus_url}{game}/mods/{mod}",
            description=f"{util_h.remove_html_tags(mod_response['summary'])}\n\n{changelog}"
        )
        message.set_author(name=mod_response["uploaded_by"], url=f"{self.nexus_url}users/{mod_response['user']['member_id']}")
        message.set_image(url=mod_response["picture_url"])
        message.set_footer(text=f"The mod was updated within the last hour")

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
            raise ChannelError("The given channel does not exist")

        if ctx.guild != channel.guild:
            raise ChannelError("The given channel is not in this server")

        config = config_h.get()
        request = urllib.request.Request(
            headers={
                "apiKey": config["nexusApiToken"],
                "User-Agent": config['apiUserAgentIdentification']
            },
            url=f"{self.api_url}games/{game}/mods/{mod}.json"
        )

        response = await web_h.read_website_content(self.client.loop, request)
        response = json.loads(response)

        if response.get("code", 200) == 404:
            raise ModError(response["message"])

        async with self.lock:
            async with self.client.db.begin() as conn:
                try:
                    await conn.execute(self.update_table.insert().values(
                        channel_id=channel.id,
                        game_domain=game,
                        mod_id=mod,
                        updated=response["updated_timestamp"]
                    ))
                except sa.exc.IntegrityError:
                    raise ModError((f"The given mod has already been subscribed to in {channel.mention}"))

        await ctx.send(f"\"{response['name']}\" Has been added to the update list in {channel.mention}")

    @commands.command(
        name="unsubscribefrommod")
    async def unsubscribe_mod(self, ctx, channel : discord.TextChannel, game : str, mod : int):
        if not channel:
            raise ChannelError("The given channel does not exist")

        if ctx.guild != channel.guild:
            raise ChannelError("The given channel is not in this server")

        async with self.lock:
            async with self.client.db.begin() as conn:
                result = await conn.execute(self.update_table.delete().where(
                    sa.and_(
                        self.update_table.c.channel_id == channel.id,
                        self.update_table.c.game_domain == game,
                        self.update_table.c.mod_id == mod
                    )
                ))

                if result.rowcount == 0:
                    raise ModError(f"There are no subscribed mods in {channel.mention} with the given parameters")

        await ctx.send(f"Mod has been removed from the update list in {channel.mention}")

    #
    # ERRORS
    #

    @subscribe_mod.error
    @unsubscribe_mod.error
    async def subscription_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(error)
        else:
            print(error)

#
# SETUP
#

def setup(client):
    client.add_cog(Nexus(client))