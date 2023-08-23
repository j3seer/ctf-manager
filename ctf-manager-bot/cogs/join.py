from discord.ext import tasks, commands
import discord
import config
import database.db as db
import helpers.checks
import time


class JoinCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(name='join', invoke_without_command=True)
    @commands.guild_only()
    async def join(self, ctx, arg):
        user_id = str(ctx.author.id)
        if arg.isnumeric():
            if not db.getUser(str(user_id)):
                db.addUser(str(user_id))
            id = arg
            if db.getEventInformationByID(id):
                event = db.getEventInformationByID(id)[0]
                event_url = event[1]
                if not config.admin_channel_id == "":
                    if db.CheckRequest(user_id, str(arg)):
                        db.addRequest(user_id, str(arg), 0)
                        admin_channel = self.client.get_channel(int(config.admin_channel_id))
                        await ctx.send(
                            "User "
                            + ctx.message.author.mention
                            + " join request has been sent to admins"
                        )
                        await admin_channel.send(
                            "User "
                            + ctx.message.author.mention
                            + "Has request to join the event:"
                            + event_url
                        )
                    else:
                        await ctx.send(
                            "Looks like you already requested to join the event "
                            + event[2]
                            + " ! Contact an admin if something went wrong!"
                        )
                else:
                    await ctx.send(
                        "Looks like you haven't added an admin channel..Check out the README.md file for configuration!"
                    )
            else:
                await ctx.send("Event not found!")
        else:
            await ctx.send("Bad command, use "+config.prefix+"cmds to check usage!")

    @join.command(name="list")
    @commands.guild_only()
    @helpers.checks.admin_channel_check(config.admin_channel_id)
    @commands.has_any_role(config.admin_role)
    async def list(self, ctx, arg=None):
        if arg:
            if arg.isnumeric():
                event_id = arg
                if db.getEventInformationByID(event_id):
                    event = db.getEventInformationByID(event_id)[0]
                    title = event[2]
                    rows = db.getRequest(event_id)
                    if rows:
                        i = 0
                        msg_out = title + " Request list:\n"
                        for request_user_id in rows:
                            i = i + 1

                            if request_user_id[1] == 1:
                                msg_out = (
                                    msg_out
                                    + str(i)
                                    + "- <@"
                                    + request_user_id[0]
                                    + "> :white_check_mark:\n"
                                )
                            else:
                                msg_out = (
                                    msg_out
                                    + str(i)
                                    + "- <@"
                                    + request_user_id[0]
                                    + "> :x:\n"
                                )
                        await ctx.send(msg_out)
                    else:
                        await ctx.send("No requests for " + title + "!")
                else:
                    await ctx.send("Event not found!")
            else:
                await ctx.send("Bad command, use "+config.prefix+"cmds to check usage!")
        else:
            rows = db.getAllRequests()
            msg_out = ""
            if rows:
                for request in rows:
                    event_id = request[1]
                    user_id_list = request[0].split(",")
                    join_state_list = request[2].split(",")
                    if db.getEventInformationByID(event_id):
                        event = db.getEventInformationByID(event_id)[0]
                        title = event[2]
                        msg_out = msg_out + "\n" + title + " Request list:\n"
                        i = 0
                        for (id, join_state) in zip(user_id_list, join_state_list):
                            i = i + 1
                            if str(join_state) == "1":
                                msg_out = (
                                    msg_out
                                    + str(i)
                                    + "- <@"
                                    + str(id)
                                    + "> :white_check_mark:\n"
                                )
                            else:
                                msg_out = msg_out + str(i) + "- <@" + str(id) + "> :x:\n"
                    else:
                        await ctx.send(
                            "Looks like the requests for the event id `"
                            + request[1]
                            + "` exist but the event has been deleted!"
                        )
                if msg_out != "":
                    await ctx.send(msg_out)
            else:
                await ctx.send("No requests found!")
            
    @join.command(name="accept")
    @commands.guild_only()
    @commands.has_any_role(config.admin_role)
    async def accept(self, ctx, arg1: discord.Member, arg2):
        user = arg1
        event_id = str(arg2)
        if event_id.isnumeric():
            # if request exist => accept
            if not db.CheckRequest(user.id, event_id):
                event = db.getEventInformationByID(event_id)[0]
                ctf_channel_id = event[5]
                ctf_channel = self.client.get_channel(int(ctf_channel_id))
                db.UpdateRequestState(user.id, event_id, 1)
                await ctf_channel.set_permissions(
                    arg1, read_messages=True
                )
                await ctx.send(
                    "Accepted <@" + str(arg1.id) + "> from event! :white_check_mark:"
                )
            else:
                await ctx.send("Request not found..:sweat_smile: Contact an admin!")
        else:
            await ctx.send("Bad command, use "+config.prefix+"cmds to check usage!")


    @join.command(name="deny")
    @commands.guild_only()
    @commands.has_any_role(config.admin_role)
    async def deny(self, ctx, arg1: discord.Member, arg2):
        user = arg1
        event_id = str(arg2)
        if event_id.isnumeric():
            # if request exist => accept
            if not db.CheckRequest(user.id, event_id):
                event = db.getEventInformationByID(event_id)[0]
                ctf_channel_id = event[5]
                ctf_channel = self.client.get_channel(int(ctf_channel_id))
                db.UpdateRequestState(user.id, event_id, 0)
                await ctf_channel.set_permissions(
                    arg1, read_messages=False, send_messages=False
                )
                await ctx.send("Denied <@" + str(arg1.id) + "> from event! :x:")
            else:
                await ctx.send("Request not found..:sweat_smile: Contact an admin!")
        else:
            await ctx.send("Bad command, use "+config.prefix+"cmds to check usage!")


async def setup(client):
    await client.add_cog(JoinCog(client))