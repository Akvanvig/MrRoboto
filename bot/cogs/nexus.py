import sqlalchemy as sa
import re
import asyncio
import json
import discord
import urllib.request

from urllib.parse import urlparse
from discord.ext import commands, tasks
from common import config_h, util_h


class HttpError(Exception):
    def __init__(self, msg = ""):
        super().__init__(msg)

class ChannelError(commands.CommandError):
    pass

class ModError(commands.CommandError):
    pass

def nexus_mod(argument):
    if not re.search(r'^[A-Za-z0-9+.\-]+://', argument):
        argument = f"https://{argument}"

    try:
        url = urlparse(argument)
    except:
        return None

    if not "nexusmods.com" in url.netloc:
        return None

    url = url._replace(query="", fragment="").path
    url = url.strip('/').split('/')

    if len(url) != 3:
        return None

    return url[0], int(url[2])

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

        mod_response = await util_h.read_website_content(request, dict)
        new_date = mod_response["updated_timestamp"]

        if new_date <= old_date:
            return None

        request = urllib.request.Request(
            headers=header,
            url=f"{self.api_url}games/{game}/mods/{mod}/changelogs.json"
        )

        mod_changelog_response = await util_h.read_website_content(request, dict)
        channel = await self.client.fetch_channel(channel_id)

        if not channel:
            raise ChannelError("Channel has been deleted")

        message = discord.Embed(
            title=mod_response["name"],
            url=f"{self.nexus_url}{game}/mods/{mod}",
            description=util_h.remove_html_tags(mod_response["summary"])
        )
        message.set_author(
            name=mod_response["uploaded_by"],
            url=f"{self.nexus_url}users/{mod_response['user']['member_id']}",
            icon_url=f"https://forums.nexusmods.com/uploads/profile/photo-thumb-{mod_response['user']['member_id']}.png"
        )

        if (versions := list(mod_changelog_response.keys())):
            version = versions[-1]
            changelog = mod_changelog_response[version]

            if len(changelog) > 10:
                changelog = changelog[:11]
                changelog[10] = "..."

            changelog[0] = f"-{changelog[0]}"

            message.add_field(
                name=f"Latest changelog [{version}]",
                value='\n-'.join(changelog),
                inline=False
            )

        message.set_image(url=mod_response["picture_url"])
        message.set_footer(text=f"This mod was updated within the last hour")

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
        name="subscribenexus",
        aliases=["subnexus"])
    async def subscribe_mod(self, ctx, mod: nexus_mod, channel: discord.TextChannel = None):
        if not mod:
            raise ModError(f"The given mod is not valid")

        if not channel:
            channel = ctx.channel
        elif ctx.guild != channel.guild:
            raise ChannelError("The given channel is not in this server")

        config = config_h.get()
        request = urllib.request.Request(
            headers={
                "apiKey": config["nexusApiToken"],
                "User-Agent": config['apiUserAgentIdentification']
            },
            url=f"{self.api_url}games/{mod[0]}/mods/{mod[1]}.json"
        )

        response = await util_h.read_website_content(request, dict)

        if response.get("code", 200) == 404:
            raise ModError(response["message"])

        async with self.lock:
            async with self.client.db.begin() as conn:
                try:
                    await conn.execute(self.update_table.insert().values(
                        channel_id=channel.id,
                        game_domain=mod[0],
                        mod_id=mod[1],
                        updated=response["updated_timestamp"]
                    ))
                except sa.exc.IntegrityError:
                    raise ModError((f"The given mod has already been subscribed to in {channel.mention}"))

        await ctx.send(f"\"{response['name']}\" has been added to the update list in {channel.mention}")

    @commands.group(
        name="unsubscribenexus",
        aliases=["unsubnexus"],
        invoke_without_command=True)
    async def unsubscribe_mod(self, ctx, mod: nexus_mod, channel: discord.TextChannel=None):
        if not mod:
            raise ModError(f"The given mod is not valid")

        if not channel:
            channel = ctx.channel
        elif ctx.guild != channel.guild:
            raise ChannelError("The given channel is not in this server")

        async with self.lock:
            async with self.client.db.begin() as conn:
                result = await conn.execute(self.update_table.delete().where(
                    sa.and_(
                        self.update_table.c.channel_id == channel.id,
                        self.update_table.c.game_domain == mod[0],
                        self.update_table.c.mod_id == mod[1]
                    )
                ))

                if result.rowcount == 0:
                    raise ModError(f"There are no subscribed mods in {channel.mention} with the given parameters")

        await ctx.send(f"The mod has been removed from the update list in {channel.mention}")

    @unsubscribe_mod.command(
        name='all')
    async def unsubscribe_mod_all(self, ctx, channel: discord.TextChannel=None):
        if not channel:
            channel = ctx.channel
        elif ctx.guild != channel.guild:
            raise ChannelError("The given channel is not in this server")

        async with self.lock:
            async with self.client.db.begin() as conn:
                result = await conn.execute(self.update_table.delete().where(
                    self.update_table.c.channel_id == channel.id
                ))

                if result.rowcount == 0:
                    raise ModError(f"There are no subscribed mods in {channel.mention}")

        await ctx.send(f"All mods have been removed from the update list in {channel.mention}")

    @commands.command(
        name="nexussubscriptions",
        aliases=["nexussubs"])
    async def list_mods(self, ctx, channel: discord.TextChannel=None):
        if not channel:
            channel = ctx.channel
        elif ctx.guild != channel.guild:
            raise ChannelError("The given channel is not in this server")

        mods = []

        async with self.lock:
            async with self.client.db.begin() as conn:
                result = await conn.stream(self.update_table.select().where(
                    self.update_table.c.channel_id == channel.id
                ))

                async for row in result:
                    mods.append(row)

        if not mods:
            raise ModError(f"There are no subscribed mods in {channel.mention}")

        mods = [f"{count} - {self.nexus_url}{mod['game_domain']}/mods/{mod['mod_id']}" for count, mod in enumerate(mods, start=1)]

        await ctx.send(f"There are {len(mods)} subscribed mods in {channel.mention}:")

        mods = '\n'.join(mods)

        for part in util_h.message_split(mods):
            await ctx.send(f"```{part}```")

    #
    # ERRORS
    #

    @subscribe_mod.error
    @unsubscribe_mod.error
    @unsubscribe_mod_all.error
    @list_mods.error
    async def subscription_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(error)
        else:
            print(error)

#
# SETUP
#

def check(client):
    config = config_h.get()

    if not client.db.exists():
        return False

    if not "nexusApiToken" in config:
        return False

    return True

@util_h.requirement_check(check)
def setup(client):
    client.add_cog(Nexus(client))