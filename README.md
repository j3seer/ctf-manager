# CTF Manager

This bot is built to make it easier to manage a large CTF team on discord, it'll be able to remind you of CTFs and manage your team's participation.
<center>
<img src="images/logo.jpg" alt="drawing" width="350"/>
</center>

# Functionalities 

### Adding a new CTF
You can add CTFs that your team will be playing

This will create a channel under the category "CTF" with the title of the CTF in CTFtime and will send generated credentials for that CTF and pin it in the channel

> **Warning**
\- THE CHANNEL WILL ONLY BE AVAILBLE TO ADMINS AT FIRST CREATION

This is intentional to keep track of who played a CTF with your team

![](/images/add_ctf.png)

The following image is from the view of a normal member / user before accepting their join request


![](/images/user_view.png)

------------
### Listing upcoming CTFs

This functionality will list CTFs that your team will participate in the future 

![](/images/list.png)
------------
### Removing and Archiving CTFs

- Archiving

![](/images/archive.png)

- Unarchiving

![](/images/unarchive.png)

You can remove CTFs by id or in bulk with `*`

![](/images/remove_bulk.png)
> **Warning**
\- DO NOT archive or remove channel by yourself (by dragging to archived ctfs category or deleting by hand), this will cause issues with the db and you'll have to clean the deleted event row by hand in the database.db file<br><br>- Removing ctfs before archiving will delete the channels



------------
### Join request

Normal users can request to join a CTF by using the join command and admins can Accept or Deny these requests

![](/images/join_request.png)

Admins will be able to accept or deny join requests

![](/images/accept_join_request.png)

Once an admin accepts a join request the user will be able to send message and check generated credentials for the CTF

![](/images/join_request2.png)

Admins can also list all requests and check their status

![](/images/join_list.png)

------------

### Bot Reminder settings

Any user can choose if they want to be reminded of the starting CTF

![](/images/reminder.png)

The reminder will be able to remind users **when the events starts** as well as:

- 8 hours before start
- 4 hours before start
- 1 hours before start
- 30 minutes before start
- 10 minutes before start

Here an example of the reminder

![](/images/reminder_example.png)


> **Warning**
\- PLEASE DO NOT ADD THE ROLE BY YOURSELF THAT'LL CREATE ISSUES WITH THE DB


------------

# Commands

> **Note**
\- * as an argument is for bulk requests (Example: `$ctf remove *` => removes all events)

### User commands
```bash
$ctf list # list all events added
$join <event_id>  # send a join request for an event
$reminder <on/off> # activate or desactive reminder for you
$ctf creds # get ctf creds of an event ( only works inside the CTF channel )
```


### Admin commands
```bash
$ctf add <ctftime_event_url> # add an event
$ctf remove <ctftime_event_id> # remove an event
$ctf remove * # remove all events
$ctf archive <ctftime_event_id> # archive an event
$ctf archive * # archive all events
$ctf unarchive <ctftime_event_id> # unarchive an event
$ctf unarchive * # unarchive all events
$join list # list all join requests
$join list <event_id> # list join request of a certain event
$join accept <username/user#id> <event_id> # accept join request
$join deny <username/user#id> <event_id> # deny join request
```

# Configurations
1- Create a bot admin role such as "ctf-manager-admin"

2- Give the bot the admin role "ctf-manager-admin"

3- Create a public bot channel and give the admin permissions to send messages

4- Create a private channel exclusive for the bot admin role 

(You can give the admin role to users who you want to add as admins)

5- Create a reminder channel visible to all members but only the admin role can send messages

6- Modify config.py


```python
# bot constants
token = "token_here" # discord token
prefix = "$"  # put prefix here
link = "https://discord.com/api/oauth2/authorize?client_id=<your_client_id>&permissions=275146599504&scope=bot"  # put bot invite link here

# admin stuff
ownerid = "your_discord_id"  # put your id here
admin_role = "ctf-manager-admin"
admin_channel_id = "admin_channel_id"

# remind settings
reminder_role = "remind-me"
reminder_role_id = "reminder_role_id"
remind_me_channel_id ="reminder_channel_id"

# team
teamname="/bin/cat" # this will be used for generated credentials
member_role="member"  
```

To get the role id of a role you need to go to server roles

![](/images/role_id.png "Role id")

To get the channel id of a channel you need to right click and "Copy channel id"

![](/images/channel_id.png "Role id")

6- Invite the bot with the permission id `275146599504`

```
https://discord.com/api/oauth2/authorize?client_id=[YOUR CLIENT ID]&permissions=275146599504&scope=bot
```

# Setup:

1- Install dependencies

```bash
$ pip3 install -r requirements
```
2- Run app.py

```bash
$ python3 app.py
```


# Files 📁

- app.py : run bot 
- db.py : SQLite database queries and setup
- checks.py : includes check functions for some commands
- utils.py : interactions with APIs / parsing / extra functions
- config.py : bot constants configuration


# Fixes / Additions 🛠️
- Add seconds to time count
- Build the `$ultimate` command
- Add reminder settings per user
- Better styling response
- Add * argument for join command to accept in bulk
- Add option to auto archive ctfs (remove from db and archive channel) if ctf ended
- Add remove from db when archiving
- Add reminder settings per user ( each user choose when to be alerted )
- Add dockerfile for deployment
- 
# Similar projects / Alternatives:

This bot is intentionally made simplistic with a few commands, I wanted to share it incase anyone was looking for a minimal bot that'll help manage their team. 

Alternative discord bots:

https://github.com/NullPxl/NullCTF

https://github.com/sigpwny/pwnybot

# Bugs 🐞

You can use github to submit a PR for suggestions or bugs, otherwise you can contact me via discord with the username `j3seer` or twitter @j3seer
