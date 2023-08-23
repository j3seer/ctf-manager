from discord.ext.commands import check, Context
import database.db as db


"""
Different check functions for commands
"""


def admin_channel_check(channel):
    async def predicate(ctx: Context):
        if str(ctx.channel.id) == str(channel):
            return True
        else:
            await ctx.send(
                "Please use the admin channel for this command! :person_gesturing_no:"
            )

    return check(predicate)


def ctf_channel_check():
    async def predicate(ctx: Context):
        if db.getCredsByChannelId(ctx.channel.id):
            return True
        else:
            await ctx.send("Please use this command in a ctf channel to get the generated credentials! :person_gesturing_no:")

    return check(predicate)