from discord.ext import tasks, commands
import discord
import database.db as db
import helpers.utils as utils
import helpers.checks as checks
import config


class ReminderCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True)
    async def reminder(self, ctx):
        await ctx.send("Bad command, use "+config.prefix+"cmds to check usage!")

    @reminder.command(name="on")
    async def on(self, ctx):
        user_id = str(ctx.author.id)
        if not db.getUser(str(user_id)):
            db.addUser(str(user_id))

        if db.ReminderSetting(user_id, "on"):
            # check if user already has the reminder role

            role = discord.utils.get(ctx.guild.roles, name=config.reminder_role)
            if role in ctx.author.roles:
                await ctx.send(
                    "CTF Reminder already turned on for user <@"
                    + str(user_id)
                    + "> :x: "
                )
            else:
                await ctx.message.author.add_roles(role)
                await ctx.send(
                    "CTF Reminder is turned on for user <@"
                    + str(user_id)
                    + "> :white_check_mark: "
                )

        else:
            await ctx.send("Something went wrong..:sweat_smile:")

    @reminder.command(name="off")
    async def off(self, ctx):
        user_id = str(ctx.author.id)
        if not db.getUser(str(user_id)):
            db.addUser(str(user_id))

        if db.ReminderSetting(user_id, "off"):
            # check if user already has the reminder role

            role = discord.utils.get(ctx.guild.roles, name=config.reminder_role)
            if not role in ctx.author.roles:
                await ctx.send(
                    "CTF Reminder already turned off for user <@"
                    + str(user_id)
                    + "> :x: "
                )
            else:
                await ctx.message.author.remove_roles(role)
                await ctx.send(
                    "CTF Reminder is turned off for user <@" + str(user_id) + "> :x: "
                )

        else:
            await ctx.send("Something went wrong..:sweat_smile:")


async def setup(client):
    await client.add_cog(ReminderCog(client))
