import discord
import platform
import pytesseract

from discord.ext import commands
from common import util_h
from io import BytesIO
from PIL import Image

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
            image_binaries.append(raw)

        if len(message := ctx.message.clean_content.split(' ', 1)) > 1:
            image_urls = []

            for line in message[1].split('\n'):
                if util_h.is_valid_url(line):
                    image_urls.append(line)

            for url in image_urls:
                try:
                    raw = await util_h.read_website_content(url)
                    image_binaries.append(raw)
                except:
                    pass

        if not image_binaries:
            # Make this a specific error
            raise Exception()

        images = []

        for raw in image_binaries:
            try:
                images.append(Image.open(BytesIO(raw)))
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
            text = pytesseract.image_to_string(image)
            cleaned_text = util_h.remove_multi_newlines(text).strip()
            split_message = util_h.message_split(text)

            split_message[0] = f"Image {i}: ```{split_message[0]}"
            split_message[-1] = f"{split_message[-1]}```"

            for part in split_message:
                await ctx.send(part)

    #
    # ERRORS
    #

    @imagetotext.error
    async def image_error(self, ctx, error):
        pass

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