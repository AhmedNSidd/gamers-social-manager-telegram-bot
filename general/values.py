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
    "Shut the fuck up you fucking pussy",
    "Can you get off Playstation's dick already?",
    "Land on me, land on three",
    "We should give Alex another chance, I'm sure he's changed. He means well now.",
    "The Great Way is not difficult for those who have no preferences. When love and hate are both absent, everything becomes clear and undisguised. Make the smallest distinction, however, and heaven and earth are set infinitely apart. If you wish to see the truth, then hold no opinions for, or against, anything."
]

help_message = """Here are the list of commands available to you:

General Commands
-------------------------------------------------------------
/help -- The bot will send this message that you're reading right now.
/quip -- The bot will hit you up with a mighty fine quip or just an okay one.
/f -- The bot will reply with a gif to help pay respect.
/mf -- The bot will reply with a sad... sad.. voice note.

Notify Commands - Send a preset message while tagging preset users
-----------------------------------------------------------------------
/add_notify_user [username without @] -- The bot will add the username to the list of people you want to notify
/del_notify_user [username without @] -- The bot will delete the username from the list of people you want to notify
/list_notify_users -- The bot will list all the users currently set for being notified when you run /notify
/set_notify_msg [message] -- The bot will set this as the message that will be sent when you run /notify
/list_notify_msg -- The bot will list the message that will be sent when you run /notify
/notify -- The bot will send the preset message while tagging the preset users.


Status Commands - Get status of players on Xbox Live and PSN.
-----------------------------------------------------------------
/add_xbox_status_user [nickname,xbox_id] -- The bot will add the users in the list of people you want the Xbox Live status for.
/del_xbox_status_user [nickname] -- The bot will delete the users from the list of people you want the Xbox Live status for.
/list_xbox_status_user -- The bot will list all the users you'll get the Xbox Live status for when you run /status
/xbox_status -- The bot will fetch the Xbox Live statuses of the set users and see if they're online.

/add_playstation_status_user [nickname,playstation_id] -- The bot will add the users in the list of people you want the PSN status for.
/del_playstation_status_user [nickname] -- The bot will delete the users from the list of people you want the PSN status for.
/list_playstation__status_user -- The bot will list all the users you'll get the PSN status for when you run /playstation_status
/playstation_status -- The bot will fetch the PSN statuses of the set users and see if they're online.
"""

birth_date = (datetime.date.today() - datetime.date(2021, 2, 8)).days

ONLINE_EMOJI = u"\U0001F7E2"
OFFLINE_EMOJI = u"\U0001F534"

ADMIN_LIST = [247340182]

BOT_URL = "https://t.me/chaddicts_bot"
HEROKU_APP_URL = "https://chaddicts-tg-bot.herokuapp.com"
TOKEN = os.environ.get("CHADDICTS_TG_BOT_TOKEN")
XBOX_CLIENT_SECRET_EXPIRY_DATE = datetime.datetime.strptime(os.environ.get("XBOX_CLIENT_SECRET_EXPIRY_DATE", "Jun 16, 2024"), "%b %d, %Y").date()

