import discord
import platform
import pytesseract

from discord.ext import commands
from common import util_h
from io import BytesIO
from PIL import Image
from functools import partial

#
# CLASSES
#

class Images(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def _images_from_ctx(self, ctx):
        image_binaries = []

        for attachment in ctx.message.attachments:
            raw = await attachment.read()
            image_binaries.append(BytesIO(raw))

        if len(message := ctx.message.clean_content.split(' ', 1)) > 1:
            image_urls = []

            for line in message[1].split('\n'):
                if util_h.is_valid_url(line):
                    image_urls.append(line)

            for url in image_urls:
                try:
                    if discord.Asset.BASE in url:
                        raw = await self.client.http.get_from_cdn(url)
                    else:
                        raw = await util_h.read_website_content(url)
                except:
                    pass
                else:
                    image_binaries.append(BytesIO(raw))

        if not image_binaries:
            # Make this a specific error
            raise Exception()

        images = []

        for bytes_io in image_binaries:
            try:
                images.append(Image.open(bytes_io))
            except:
                pass

        if not images:
            # Make this a specific error
            raise Exception()

        return images

    #
    # COMMANDS
    #

    @commands.command(
        name="imagetotext")
    async def imagetotext(self, ctx):
        # Document this
        images = await self._images_from_ctx(ctx)

        for i, image in enumerate(images, 1):
            image_partial = partial(pytesseract.image_to_string, image, lang='nor+eng+jpn+ara+kor')

            text = await self.client.loop.run_in_executor(None, image_partial)
            cleaned_text = util_h.remove_multi_newlines(text).strip()

            if not cleaned_text:
                await ctx.send(f"Image {i}: No text detected")
                continue

            split_message = util_h.message_split(cleaned_text)
            split_message = [f"```{part}```" for part in split_message]
            split_message[0] = f"Image {i}: {split_message[0]}"

            for part in split_message:
                await ctx.send(part)

    #
    # ERRORS
    #

    @imagetotext.error
    async def image_error(self, ctx, error):
        await ctx.send(error)

#
# SETUP
#

def check(client):
    # Disable on windows for now
    # as there is easily accessible tesseract binary on Windows
    if platform.system() != "Linux":
        return False

    return True

@util_h.requirement_check(check)
def setup(client):
    client.add_cog(Images(client))
