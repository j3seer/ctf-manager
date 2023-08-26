from discord.ext import tasks, commands
import discord
import time
import config
import asyncio
import time
import database.db as db
import helpers.utils as utils
from aiostream import stream, pipe

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(
    command_prefix=commands.when_mentioned_or(config.prefix), intents=intents
)


@client.command(name="ping")
async def ping(ctx):
    """See if The Bot is Working"""
    pingtime = time.time()
    pingms = await ctx.send("Pinging...")
    ping = time.time() - pingtime
    pingedited = ":ping_pong:  time is `%.01f seconds`" % ping
    # print(pingedited)
    await pingms.edit(content=pingedited)


@client.command(name="cmds")
async def cmds(ctx, *args):
    """List all available commands"""
    await ctx.send(
        content="""All available commands:`ctf list`,`join <event_id>`,`reminder <on/off>`, 
        `ctf remove <event_id>`,`join accept <username> <event_id>`,`join deny <username> <event_id>`,`join list`"""
    )


@client.event
async def on_ready():
    print("----------------------")
    print("Logged In As")
    print("Username: %s" % client.user.name)
    print("ID: %s" % client.user.id)
    print("----------------------")


@client.event
async def on_command_error(ctx, err: Exception) -> None:
    if isinstance(err, commands.errors.CommandNotFound):
        pass
    elif isinstance(err, discord.errors.NotFound):
        pass
    elif isinstance(err, discord.errors.Forbidden):
        await ctx.send("Forbidden :person_gesturing_no:")
    elif isinstance(err, commands.errors.MissingPermissions):
        await ctx.send("Permission denied :person_gesturing_no:")
    elif isinstance(err, commands.errors.MissingAnyRole):
        await ctx.send("Permission denied :person_gesturing_no:")
    elif isinstance(err, commands.errors.BotMissingPermissions):
        await ctx.send("No privileges to perform this action :person_gesturing_no:")
    elif isinstance(err, commands.errors.NoPrivateMessage):
        await ctx.send("Can't use DM for issuing commands :person_gesturing_no:")
    else:
        print(err)
        # await ctx.send("Not sure what happened..but something went wrong :sweat_smile:")


""" reminder bg task.loop """


@tasks.loop(seconds=1)
async def remind(client):
    events = db.getEvents()
    if events:
        # convert events list to iterable for async for loops
        events_stream = stream.iterate(events) | pipe.map(
            utils.check_time, ordered=True, task_limit=10
        )
        async for event in events_stream:
            channel = client.get_channel(int(config.remind_me_channel_id))
            if event:
                if event[0] == 0:
                    title = event[1]
                    await channel.send(
                        "<@&"
                        + config.reminder_role_id
                        + "> The CTF event `"
                        + str(title)
                        + "` just started `right now!` :white_check_mark:"
                    )
                elif event[0] == 30:
                    title = event[1]
                    await channel.send(
                        "<@&"
                        + config.reminder_role_id
                        + "> The CTF event `"
                        + str(title)
                        + "` starts in `"
                        + str(event[0])
                        + " Minutes!` :timer: "
                    )
                elif event[0] == 60:
                    title = event[1]
                    await channel.send(
                        "<@&"
                        + config.reminder_role_id
                        + "> The CTF event `"
                        + str(title)
                        + "` starts in `1 Hour` :timer: "
                    )
                elif event[0] == (60 * 4):
                    title = event[1]
                    await channel.send(
                        "<@&"
                        + config.reminder_role_id
                        + "> The CTF event `"
                        + str(title)
                        + "` starts in `4 Hours` :timer: "
                    )
                elif event[0] == (60 * 8):
                    title = event[1]
                    await channel.send(
                        "<@&"
                        + config.reminder_role_id
                        + "> The CTF event `"
                        + str(title)
                        + "` starts in `8 Hours` :timer: "
                    )
            else:
                pass

    else:
        pass


@remind.before_loop
async def before():
    await client.wait_until_ready()
    #print("Finished waiting")


extensions = ["reminder", "cat", "join", "ctf"]  # Add more cogs as needed


async def load_extensions():
    for extension in extensions:
        await client.load_extension(f"cogs.{extension}")


async def main():
    async with client:
        discord.utils.setup_logging()
        await load_extensions()
        remind.start(client)
        await client.start(config.token)


asyncio.run(main())
