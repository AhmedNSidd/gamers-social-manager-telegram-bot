import datetime
import os

quips = [
    "How bout you align your chakras before coming at me with that poison",
    "You realize Steve Jobs is spying on you right? That every little camera in that phone is a hole for Jobs to peep your peep while you sleep?",
    "What are you doing step bro...",
    "To be fair, you do have to have a very high IQ to meditate.",
    "Imagine making meditation your entire personality.",
    "Imagine not making meditation your entire personality",
    "The only thing falling faster than the GME stock is Ahmed's grades.",
    "Sorry, I don't watch tiktok. I'm not a virgin.",
    "IT'S A FUCKING JOKE MAN! HAHAHA",
    "ASS!",
    "Shut the fuck up you fucking pussy"
]

help_message = """Here are the list of commands available to you:

General Commands
/help -- The bot will send this message that you're reading right now.
/quip -- The bot will hit you up with a mighty fine quip or just an okay one.

Notify Commands | Send a preset message while tagging preset users
/add_notify_user [username without @] -- The bot will add the username to the list of people you want to notify
/del_notify_user [username without @] -- The bot will delete the username from the list of people you want to notify
/list_notify_users -- The bot will list all the users currently set for being notified when you run /notify
/set_notify_msg [message] -- The bot will set this as the message that will be sent when you run /notify
/list_notify_msg -- The bot will list the message that will be sent when you run /notify
/notify -- The bot will send the preset message while tagging the preset users.


Status Commands | Get status of players on Xbox Live.
/add_status_user [nickname,xuid] -- The bot will add the users in the list of people you want the status for.
/del_status_user [nickname] -- The bot will delete the users from the list of people you want the status for.
/list_status_user -- The bot will list all the users you'll get the status for when you run /status
/status -- The bot will fetch the Xbox Live status of chad gamers and see if they're online.
"""

birth_date = (datetime.date.today() - datetime.date(2021, 2, 8)).days

ONLINE_EMOJI = u"\U0001F7E2"
OFFLINE_EMOJI = u"\U0001F534"

PROJECT_PATH = os.getcwd()
NOTIFY_DB = os.path.join(PROJECT_PATH, "db/notify.json")
STATUS_DB = os.path.join(PROJECT_PATH, "db/status.json")
