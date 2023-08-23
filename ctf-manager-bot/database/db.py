import sqlite3
from sqlite3 import Error
import config
import os

conn = None

try:
    if not os.path.isfile("database/database.db"):
        # if db doesnt exist: create and initialize it again
        db_file = open("database/database.db", "w")
        # connect to newly created db file
        conn = sqlite3.connect("database/database.db")
        with open("database/init.sql") as f:
            # initialize db tables
            conn.executescript(f.read())
            # store owner
            cur = conn.cursor()
            cur.execute(
                f'INSERT OR IGNORE INTO users (user_id, reminder, reminder_settings) VALUES ("{config.ownerid}", FALSE , "");'
            )  
            conn.commit() 
    else:
        # connect to existing db
        conn = sqlite3.connect("database/database.db")
except Error as e:
    print(e)


def getEvents():
    cur = conn.cursor()
    query = "SELECT * from events"
    results = cur.execute(query).fetchall()
    conn.commit()
    return results

def UpdateEndingStatus(event_id):
    cur = conn.cursor()
    query = "UPDATE events SET ended_status = 1 where event_id=?"
    results = cur.execute(query,(event_id,)).fetchone()
    conn.commit()
    return results

def StartingSoon():
    cur = conn.cursor()
    query = "SELECT * from events where ended_status = 0"
    results = cur.execute(query).fetchall()
    conn.commit()
    return results

def RemoveAllEvents():
    cur = conn.cursor()
    query = "DELETE FROM events;"
    results = cur.execute(query).fetchall()
    conn.commit()
    return results

def getEventInformationByID(id):
    cur = conn.cursor()
    query = "SELECT * from events where event_id=?"
    results = cur.execute(query, (id,)).fetchall()
    conn.commit()
    return results


def getEventChannelTitle(event_url):
    cur = conn.cursor()
    query = "SELECT channel_name from events where event_url=?"
    results = cur.execute(query, (event_url,)).fetchone()
    conn.commit()
    return results


def addEvent(event_id, url, event, channel_id, channel_name,ctf_password):
    cur = conn.cursor()
    query = "INSERT INTO events (event_id, event_url, event_title, time_start, time_finish, channel_id, channel_name, ctf_password) VALUES (?,?,?,?,?,?,?,?)"
    results = cur.execute(
        query,
        (
            event_id,
            url,
            event[0]["title"],
            event[0]["start"],
            event[0]["finish"],
            channel_id,
            channel_name,
            ctf_password
        ),
    )
    conn.commit()
    return results


def RemoveEvent(id):
    cur = conn.cursor()
    query = "DELETE FROM events WHERE event_id=?"
    cur.execute(query, (id,))
    conn.commit()

    query = "REINDEX events;"
    cur.execute(query)
    conn.commit()


def getUser(user_id):
    cur = conn.cursor()
    query = "SELECT * from users where user_id=?"
    results = cur.execute(query, (user_id,)).fetchone()
    conn.commit()
    return results


def addUser(user_id):
    cur = conn.cursor()
    query = "INSERT INTO users (user_id) VALUES (?)"
    results = cur.execute(query, (user_id,))
    conn.commit()
    return results


def ReminderSetting(user_id, option):
    cur = conn.cursor()
    if getUser(user_id):
        if option == "on":
            query = "UPDATE users SET reminder = 1 where user_id=?"
            cur.execute(query, (user_id,)).fetchone()
            conn.commit()
            return 1
        elif option == "off":
            query = "UPDATE users SET reminder = 0 where user_id=?"
            cur.execute(query, (user_id,)).fetchone()
            conn.commit()
            return 1
    else:
        return "lol"


def addRequest(user_id, event_id, state):
    cur = conn.cursor()
    query = "INSERT INTO join_requests (user_id,event_id) VALUES (?,?)"
    results = cur.execute(
        query,
        (
            user_id,
            event_id,
        ),
    )
    conn.commit()
    return results


def CheckRequest(user_id, event_id):
    cur = conn.cursor()
    query = "SELECT * from join_requests where user_id=? and event_id=?"
    results = cur.execute(query, (user_id, event_id)).fetchall()
    conn.commit()
    if results:
        return 0
    else:
        return 1


def UpdateRequestState(user_id, event_id, state):
    cur = conn.cursor()
    if state:
        query = "UPDATE join_requests SET join_state = 1 where user_id=? and event_id=?"
        results = cur.execute(
            query,
            (
                user_id,
                event_id,
            ),
        )
        conn.commit()
        return results
    else:
        query = "UPDATE join_requests SET join_state = 0 where user_id=? and event_id=?"
        results = cur.execute(
            query,
            (
                user_id,
                event_id,
            ),
        )
        conn.commit()
        return results


def CheckRequestState(user_id, event_id):
    cur = conn.cursor()
    query = "SELECT join_state from join_requests where user_id=? and event_id=?"
    results = cur.execute(
        query,
        (
            user_id,
            event_id,
        ),
    ).fetchone()
    conn.commit()
    return results[0]


def getRequest(event_id):
    cur = conn.cursor()
    query = "SELECT user_id,join_state from join_requests where event_id=?"
    results = cur.execute(query, (event_id,)).fetchall()
    conn.commit()
    return results


def getAllRequests():
    cur = conn.cursor()
    query = "SELECT group_concat(user_id),event_id,group_concat(join_state) from join_requests GROUP BY event_id;"
    results = cur.execute(query).fetchall()
    conn.commit()
    return results


def RemoveAllRequests():
    cur = conn.cursor()
    query = "DELETE FROM join_requests;"
    results = cur.execute(query).fetchall()
    conn.commit()
    return results

def RemoveRequestByID(event_id):
    cur = conn.cursor()
    query = "DELETE FROM join_requests WHERE event_id=?;"
    results = cur.execute(query, (event_id,))
    conn.commit()
    return results

def getCredsByChannelId(channel_id):
    cur = conn.cursor()
    query = "SELECT ctf_password FROM events where channel_id=?;"
    results = cur.execute(query, (channel_id,)).fetchone()
    conn.commit()
    return results

def UpdateArchiveStatus(archived_status,channel_id):
    cur = conn.cursor()
    query = "UPDATE events SET archived = ? where channel_id=?;"
    results = cur.execute(query, (archived_status,channel_id,)).fetchone()
    conn.commit()
    return results

def GetArchiveStatus(event_id):
    cur = conn.cursor()
    query = "SELECT archived from events where event_id=?;"
    results = cur.execute(query, (event_id,)).fetchone()
    conn.commit()
    return results

def GetEndedStatus():
    cur = conn.cursor()
    query = "SELECT ended_status from events;"
    results = cur.execute(query).fetchall()
    conn.commit()
    return results

