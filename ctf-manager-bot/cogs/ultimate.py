"""
give ultimate sick payloads for certain topics

example:

$ultimate "ssti" => {{config...
$ultimate "xss" => 10 different filter bypasses
$ultimate "sqli" => 10 different filter bypasses
"""

from discord.ext import tasks, commands
import database.db as db
import helpers.utils as utils
import helpers.checks as checks
import config


class UltimateCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True)
    async def ultimate(self, ctx):
        await ctx.send("Bad command, use "+config.prefix+"cmds to check usage!")


async def setup(client):
    await client.add_cog(UltimateCog(client))