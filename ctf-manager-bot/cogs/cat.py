from discord.ext import commands
import database.db as db
import helpers.utils as utils
import helpers.checks as checks
import asyncio


class CatCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True)
    async def cat(self, ctx, *args):
        # Your main command code here
        try:
            msg = await ctx.send(
                "Loading a cat picture :arrows_counterclockwise: :cat2:"
            )
            url = utils.getcat()
            await asyncio.sleep(2)
            await msg.edit(content=str(url))
        except:
            await ctx.send("Something went wrong..:x:")


async def setup(client):
    await client.add_cog(CatCog(client))