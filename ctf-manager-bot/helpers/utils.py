import re
import requests
import maya
from datetime import date, datetime, time, timezone, timedelta
from babel.dates import format_date, format_datetime, format_time
import urllib.parse
import database.db as db
import random
import secrets

pattern = r"^https:\/\/ctftime\.org\/event\/\d+$"

test_url = "https://ctftime.org/event/2064"

api = "https://ctftime.org/api/v1/"


def check_url(url):
    if re.match(pattern, url):
        return 1
    else:
        return 0


def check_time(event):
    title = event[2]
    start = event[3]
    start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
    current_time = datetime.now(timezone.utc).replace(microsecond=0)
    diff = (start_dt - current_time).total_seconds() / 60

    if diff == 30:  # half an hour before start
        return 30, title
    elif diff == 60:  # hour before start
        return 60, title
    elif diff == (60 * 4):  # 4 hours before start
        return (60 * 4), title
    elif diff == (60 * 8):  # 8 hours before start
        return (60 * 8), title
    elif diff == 0.0:
        return 0, title


def detect_ended(start, finish):
    start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
    finish_dt = datetime.strptime(finish, "%Y-%m-%dT%H:%M:%S%z")
    current_time = datetime.now(timezone.utc)

    if current_time > finish_dt:
        return 0
    else:
        return 1


def timeleft(start, finish, event_id):
    start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
    finish_dt = datetime.strptime(finish, "%Y-%m-%dT%H:%M:%S%z")
    current_time = datetime.now(timezone.utc)

    if current_time > finish_dt:
        db.UpdateEndingStatus(event_id)
        return "```diff\n- This event already ended```"
    elif current_time > start_dt and current_time < finish_dt:
        timeleft = str(finish_dt - current_time)
        if "days" in timeleft or "day" in timeleft:
            days_str, time_str = timeleft.split(", ")
            time_components = time_str.split(":")
            days = int(days_str.split()[0])
            hours = int(time_components[0])
            minutes = int(time_components[1])
            output_format = f"{days} Days, {hours} Hours, {minutes} Minutes"
        else:
            time_components = timeleft.split(":")
            hours = int(time_components[0])
            minutes = int(time_components[1])
            output_format = f"{hours} Hours, {minutes} Minutes"
        return (
            "```fix\nCTF currently running, Ending in : " + str(output_format) + "```"
        )
    else:
        timeleft = str(start_dt - current_time)
        if "days" in timeleft or "day" in timeleft:
            days_str, time_str = timeleft.split(", ")
            time_components = time_str.split(":")
            days = int(days_str.split()[0])
            hours = int(time_components[0])
            minutes = int(time_components[1])
            output_format = f"{days} Days, {hours} Hours, {minutes} Minutes"
        else:
            time_components = timeleft.split(":")
            hours = int(time_components[0])
            minutes = int(time_components[1])
            output_format = f"{hours} Hours, {minutes} Minutes"
        return "```diff\n+ Starts in: " + str(output_format) + "```"


def time_parse(t):
    dt      = maya.parse(t).datetime()
    date_dt = str(dt.date())
    d       = date(int(date_dt[0:4]), int(date_dt[5:7]), int(date_dt[8:]))
    time    = dt.time().strftime("%I:%M%p")
    region  = dt.tzinfo
    return format_date(d, "dd MMMM", locale="en"), time, str(region)


def get_event_information(url):
    event_id = url[26:]
    events_info_api = api + "events/" + event_id + "/"
    r = requests.get(events_info_api, headers="")
    if r.status_code == 404:
        return 0
    else:
        event_infos = r.json()
        # start date
        start = event_infos["start"]
        # finish date
        finish = event_infos["finish"]
        return event_infos, start, finish


def get_event_name(url):
    if re.match(pattern, url):
        return 1
    else:
        return 0


def generate_password():
    password = secrets.token_urlsafe(nbytes=32)
    return password


def search_channel(ctx, id):
    for channel in ctx.guild.channels:
        if channel.id == int(id):
            return channel.id
    return False


def search_category(ctx, discord, category_name):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name=category_name)
    if category is None:
        return 0
    else:
        return category


def getcat():
    wordlist = [
        "bincatz!",
        "cat attack!",
        "el gato",
        "cat invasion!",
        "little boi",
        "potato",
    ]
    url = (
        "https://cataas.com/cat/says/"
        + urllib.parse.quote(random.choice(wordlist))
        + "?size=50"
    )
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            return url
    except:
        return 0


def test_func(x):
    if check_url(x):
        get_event_information(x)


"""
# Remove quotes to test utils
test_func(test_url)
"""