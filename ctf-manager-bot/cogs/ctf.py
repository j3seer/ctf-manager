from discord.ext import tasks, commands
import discord
import config
import database.db as db
import helpers.utils as utils
import helpers.checks as checks
import asyncio
from typing import Union
from datetime import date, datetime, time, timezone, timedelta


class CTFCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.ctf_category_name = "CTF"
        self.archived_ctf_category_name = "archive ctfs " + str(datetime.now().year)

    @commands.group(name="ctf", invoke_without_command=True)
    @commands.guild_only()
    async def ctf(self, ctx):
        await ctx.send("Bad command, use "+config.prefix+"cmds to check usage!")

    @ctf.command(name="list")
    @commands.guild_only()
    async def list(self, ctx):
        """list: List CTF Events"""
        rows = db.getEvents()
        if rows:
            msg_out = ""
            for event in rows:
                id = str(event[0])
                url = event[1]
                title = event[2]
                start = event[3]
                finish = event[4]
                timeleft = utils.timeleft(start, finish, id)
                start_msg = (
                    "Starting: "
                    + utils.time_parse(start)[0]
                    + " - "
                    + utils.time_parse(start)[1]
                    + " "
                    + utils.time_parse(start)[2]
                )
                finish_msg = (
                    "Finishing: "
                    + utils.time_parse(finish)[0]
                    + " - "
                    + utils.time_parse(finish)[1]
                    + " "
                    + utils.time_parse(finish)[2]
                )
                msg_out = (
                    msg_out
                    + "```ini\n["
                    + id
                    + "] "
                    + title
                    + "\n"
                    + url
                    + "\n"
                    + start_msg
                    + "\n"
                    + finish_msg
                    + "```\n"
                    + str(timeleft)
                    + "\nUse `"+config.prefix+"join "
                    + id
                    + "`to send a join request to the CTF channel\n\n"
                )
            await ctx.send("List of future CTFs:\n" + msg_out)
        else:
            await ctx.send("No future CTFs on the list")

    @ctf.command(name="add")
    @commands.guild_only()
    @checks.admin_channel_check(config.admin_channel_id)
    @commands.has_any_role(config.admin_role)
    async def add(self, ctx, arg):
        """add <url>: Add CTF Event to the reminding list"""
        event_url = arg
        if utils.check_url(event_url):
            event = utils.get_event_information(event_url)
            if event:
                event_id = event[0]["id"]
                title = event[0]["title"]
                start = event[0]["start"]
                finish = event[0]["finish"]
                if utils.detect_ended(start, finish):

                    if not db.getEventInformationByID(event_id):  # doesnt exist in db

                        if not utils.search_category(
                            ctx, discord, self.ctf_category_name
                        ):
                            # create category
                            await ctx.guild.create_category(self.ctf_category_name)

                        # get category object
                        category = utils.search_category(
                            ctx, discord, self.ctf_category_name
                        )

                        # cateogry default access permissions only for bot and bot admins
                        admin_role = discord.utils.get(
                            ctx.guild.roles, name=config.admin_role
                        )
                        bot_role = discord.utils.get(
                            ctx.guild.roles, name="ctf-manager"
                        )
                        member_role = discord.utils.get(
                            ctx.guild.roles, name=config.member_role
                        )

                        everyone_else = discord.utils.get(
                            ctx.guild.roles, name="@everyone"
                        )
                        await category.set_permissions(
                            member_role, read_messages=False, send_messages=True
                        )
                        await category.set_permissions(
                            admin_role, read_messages=True, send_messages=True
                        )
                        await category.set_permissions(
                            bot_role, read_messages=True, send_messages=True
                        )
                        await category.set_permissions(
                            everyone_else, read_messages=False, send_messages=False
                        )
                        # create channel under category
                        channel = await ctx.guild.create_text_channel(
                            name=title, category=category
                        )
                        channel_id = channel.id
                        channel_name = channel.name
                        # generate creds

                        password = utils.generate_password()
                        message = await channel.send(
                            "Generated credentials:\nusername=`"
                            + str(config.teamname)
                            + "`\npassword=`"
                            + str(password)
                            + "` "
                        )

                        # pin message in ctf channel

                        await message.pin()

                        # store channel id and name in DB
                        db.addEvent(
                            event_id,
                            event_url,
                            event,
                            str(channel_id),
                            str(channel_name),
                            str(password),
                        )

                        await ctx.send(
                            "```ini\nAdded the event ["
                            + title
                            + "] to the list of future CTFs```\nCreated the channel <#"
                            + str(channel_id)
                            + ">"
                        )

                    else:
                        await ctx.send(
                            "```ini\nLooks like the event ["
                            + title
                            + "] has already been added```"
                        )
                else:
                    await ctx.send(
                        "```ini\nLooks like this event has already ended..```"
                    )
            else:
                await ctx.send("```ini\nEvent not found, check submitted URL!```")
        else:
            await ctx.send(
                "Bad URL, make sure to use a link such as `https://ctftime.org/event/1234`"
            )

    @ctf.command(name="remove")
    @commands.guild_only()
    @checks.admin_channel_check(config.admin_channel_id)
    @commands.has_any_role(config.admin_role)
    async def remove(self, ctx, arg):
        """remove <event_id>: Remove CTF Event"""
        id = str(arg)
        if id != "*":
            if db.getEventInformationByID(id):  # if exist in db
                # remove channel
                info = db.getEventInformationByID(int(id))
                title = info[0][2]
                channel_id = info[0][5]
                channel = self.client.get_channel(int(channel_id))
                print(db.GetArchiveStatus(id))

                if channel:
                    if not db.GetArchiveStatus(id)[0]:
                        # remove event data and join request from db
                        await channel.delete()
                        db.RemoveEvent(id)
                        db.RemoveRequestByID(id)
                        await ctx.send(
                            "Removed the event `"
                            + title
                            + "` in the list of future CTFs"
                        )
                    else:
                        await ctx.send(
                            "The event `"
                            + title
                            + "` is archived, can't remove archived events!"
                        )
                else:
                    await ctx.send(
                        "Looks like the channel for the event `"
                        + title
                        + "` is already deleted!"
                    )
            else:
                await ctx.send(
                    "Looks like the event `" + arg + "` you're looking for don't exist!"
                )
        else:
            # check if db has events in the first place
            if db.getEvents():
                await ctx.send(
                    "Are you sure you want all events deleted? :thinking: \nReact with :white_check_mark: on this message to confirm or :x: to deny!"
                )

                # check for reaction type ✅ or ❌
                def check(r: discord.Reaction, u: Union[discord.Member, discord.User]):
                    return (
                        u.id == ctx.author.id
                        and r.message.channel.id == ctx.channel.id
                        and str(r.emoji) in ["\U00002705", "\U0000274c"]
                    )

                try:
                    reaction, user = await self.client.wait_for(
                        "reaction_add", check=check, timeout=120.0
                    )

                except asyncio.TimeoutError:
                    # at this point, the check didn't become True.
                    await ctx.send(
                        "Reaction timeout! Reuse the command to initiate again!"
                    )
                    return
                else:

                    # unicode for ✅ :
                    # https://emojipedia.org/emoji/✅/#:~:text=Codepoints

                    if str(reaction.emoji) == "\U00002705":
                        already_deleted = []
                        events = db.getEvents()
                        for row in events:
                            event_id = row[0]
                            title = row[2]
                            if not db.GetArchiveStatus(event_id)[0]:
                                channel_id = row[5]
                                channel_name = row[2]
                                channel = self.client.get_channel(int(channel_id))
                                if channel:
                                    await channel.delete()
                                else:
                                    # if issue with channel save it for output
                                    already_deleted.append(str(channel_name))

                                db.RemoveAllEvents()
                                db.RemoveAllRequests()
                                if len(already_deleted) > 0:
                                    return await ctx.send(
                                        "Succesfully Removed all events ✅ !\nIn the process of removal, the following channels `"
                                        + str(*already_deleted)
                                        + "` can't be found! Assuming these channels have already been deleted!"
                                    )
                                else:
                                    return await ctx.send(
                                        "Succesfully Removed all events ✅ !"
                                    )
                            else:
                                await ctx.send(
                                    "The event `"
                                    + title
                                    + "` is archived, can't remove archived events!"
                                )

                    # unicode for ❌ :
                    # https://emojipedia.org/emoji/❌/#:~:text=Codepoints
                    if str(reaction.emoji) == "\U0000274c":
                        return await ctx.send("Denied Removal of all events ❌ !")
            elif not len(arg):
                return await ctx.send("Please provide an event id!")
            else:
                return await ctx.send("Looks like there are no events found!")

    @ctf.command(name="creds")
    @commands.guild_only()
    @checks.ctf_channel_check()
    async def creds(self, ctx):
        """creds: get creds of a ctf"""

        cred = db.getCredsByChannelId(str(ctx.channel.id))
        await ctx.send(
            "Credentials:\nusername: `"
            + config.teamname
            + "`\npassword: `"
            + str(cred[0])
            + "`"
        )
        # await ctx.send("Get credentials command!")

    async def create_category(self, ctx, name, members_read, members_send):
        members = discord.utils.get(ctx.guild.roles, name=config.member_role)
        archived_category = await ctx.guild.create_category(name)
        admin_role = discord.utils.get(ctx.guild.roles, name=config.admin_role)
        # set correct permissions
        await archived_category.set_permissions(
            members, read_messages=members_read, send_messages=members_send
        )

    @ctf.command(name="archive")
    @commands.guild_only()
    @checks.admin_channel_check(config.admin_channel_id)
    @commands.has_any_role(config.admin_role)
    async def archive(self, ctx, arg):
        """archive <event_id>: Archive CTF Event by moving the event channel to the archived category and give all members permissions to read message but not send messages"""
        event_id = arg
        if arg.isnumeric():
            event = db.getEventInformationByID(event_id)
            if event:
                # create archived category if it doesnt exist
                if not utils.search_category(
                    ctx, discord, self.archived_ctf_category_name
                ):
                    await self.create_category(
                        ctx, self.archived_ctf_category_name, True, False
                    )

                # get category object
                archived_category = utils.search_category(
                    ctx, discord, self.archived_ctf_category_name
                )
                members = discord.utils.get(ctx.guild.roles, name=config.member_role)

                # get ctf channel and modify it's permissions to allow all members to read message only
                ctf_channel = self.client.get_channel(int(event[0][5]))
                ctf_channel_permissions = ctf_channel.overwrites
                new_permission = discord.PermissionOverwrite()
                new_permission.read_messages = (
                    True  # You can set other permissions as needed
                )
                new_permission.send_messages = False
                ctf_channel_permissions[members] = new_permission

                # move ctf channel to archived category and change permissions
                await ctf_channel.edit(
                    category=archived_category, overwrites=ctf_channel_permissions
                )

                await ctx.send("Archived the following CTF: `" + event[0][2] + "`")
                db.UpdateArchiveStatus(1, event[0][5])
            else:
                await ctx.send("Looks like this event does not exist! :x:")
        elif str(arg) == "*":
            events = db.getEvents()
            if events:
                for event in events:
                    # create archived category if it doesnt exist
                    if not utils.search_category(
                        ctx, discord, self.archived_ctf_category_name
                    ):
                        await self.create_category(
                            ctx, self.archived_ctf_category_name, True, False
                        )

                    # get category object
                    archived_category = utils.search_category(
                        ctx, discord, self.archived_ctf_category_name
                    )
                    members = discord.utils.get(
                        ctx.guild.roles, name=config.member_role
                    )

                    # get ctf channel and modify it's permissions to allow all members to read message only
                    ctf_channel = self.client.get_channel(int(event[0][5]))
                    ctf_channel_permissions = ctf_channel.overwrites
                    new_permission = discord.PermissionOverwrite()
                    new_permission.read_messages = (
                        True  # You can set other permissions as needed
                    )
                    new_permission.send_messages = False
                    ctf_channel_permissions[members] = new_permission

                    # move ctf channel to archived category and change permissions
                    await ctf_channel.edit(
                        category=archived_category, overwrites=ctf_channel_permissions
                    )

                    await ctx.send("Archived the following CTF: `" + event[2] + "`")
                    db.UpdateArchiveStatus(1, event[5])

            else:
                await ctx.send("Looks like there are no existing events! :x:")
        else:
            await ctx.send("Something went wrong..:sweat_smile:")

    @ctf.command(name="unarchive")
    @commands.guild_only()
    @checks.admin_channel_check(config.admin_channel_id)
    @commands.has_any_role(config.admin_role)
    async def unarchive(self, ctx, arg):
        """unarchive <event_id>: unarchive an archived CTF Event by moving the event channel to the CTF category and setting permissions to users that joined the event"""
        event_id = arg
        if arg.isnumeric():
            event = db.getEventInformationByID(event_id)
            if event:
                archived_status = event[0][9]
                title = event[0][2]
                if archived_status:
                    if not utils.search_category(ctx, discord, self.ctf_category_name):
                        await self.create_category(
                            ctx, self.ctf_category_name, False, False
                        )

                    ctf_category = utils.search_category(
                        ctx, discord, self.ctf_category_name
                    )
                    members = discord.utils.get(
                        ctx.guild.roles, name=config.member_role
                    )
                    # get ctf channel and modify it's permissions to deny all members from reading messages. Only already joined members can read and send messages
                    ctf_channel = self.client.get_channel(int(event[0][5]))
                    ctf_channel_permissions = ctf_channel.overwrites
                    new_permission = discord.PermissionOverwrite()
                    new_permission.read_messages = False
                    new_permission.send_messages = True
                    ctf_channel_permissions[members] = new_permission

                    # move ctf channel to archived category and change permissions
                    await ctf_channel.edit(
                        category=ctf_category, overwrites=ctf_channel_permissions
                    )

                    await ctx.send(
                        "Unarchived the following CTF: `" + event[0][2] + "`"
                    )
                    db.UpdateArchiveStatus(0, event[0][5])
                else:
                    await ctx.send(
                        "Looks like the event `" + title + "` isn' archived! :x:"
                    )
            else:
                await ctx.send("Looks like this event does not exist! :x:")
        elif str(arg) == "*":
            events = db.getEvents()
            if events:
                for event in events:
                    title = event[2]
                    archived_status = event[9]
                    if archived_status:
                        if not utils.search_category(
                            ctx, discord, self.ctf_category_name
                        ):
                            await self.create_category(
                                ctx, self.ctf_category_name, False, False
                            )

                        ctf_category = utils.search_category(
                            ctx, discord, self.ctf_category_name
                        )
                        members = discord.utils.get(
                            ctx.guild.roles, name=config.member_role
                        )
                        # get ctf channel and modify it's permissions to deny all members from reading messages. Only already joined members can read and send messages
                        ctf_channel = self.client.get_channel(int(event[5]))
                        ctf_channel_permissions = ctf_channel.overwrites
                        new_permission = discord.PermissionOverwrite()
                        new_permission.read_messages = False
                        new_permission.send_messages = True
                        ctf_channel_permissions[members] = new_permission

                        # move ctf channel to archived category and change permissions
                        await ctf_channel.edit(
                            category=ctf_category, overwrites=ctf_channel_permissions
                        )

                        await ctx.send(
                            "Unarchived the following CTF: `" + event[2] + "`"
                        )
                        db.UpdateArchiveStatus(0, event[5])
                    else:
                        await ctx.send(
                            "Looks like the event `" + title + "` isn' archived! :x:"
                        )
            else:
                await ctx.send("Looks like there are no existing events! :x:")
        else:
            await ctx.send("Something went wrong..:sweat_smile:")


async def setup(client):
    await client.add_cog(CTFCog(client))