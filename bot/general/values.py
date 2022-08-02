import datetime
import humanize
import os


help_message = """Here are the list of commands available to you:

General Commands
-------------------------------------------------------------
/help -- The bot will send this message that you're reading right now.
/quip -- The bot will hit you up with a mighty fine quip or just an okay one.
/f -- The bot will reply with a gif to help pay respect.
/mf -- The bot will reply with a sad... sad.. voice note.
/age -- The bot will reply with how old the bot is.

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
/add_xbox_status gamertag1, gamertag2, ... -- The bot will add the users in the list of people you want the Xbox Live status for.
/del_xbox_status gamertag1, gamertag2, ... -- The bot will delete the users from the list of people you want the Xbox Live status for.
/list_xbox_status -- The bot will list all the users you'll get the Xbox Live status for when you run /xbox_status
/xbox_status -- The bot will fetch the Xbox Live statuses of the set users and see if they're online.

/add_playstation_status psn_online_id1, psn_online_id1, ... -- The bot will add the users in the list of people you want the PSN status for.
/del_playstation_status psn_online_id1, psn_online_id1, ... -- The bot will delete the users from the list of people you want the PSN status for.
/list_playstation__status -- The bot will list all the users you'll get the PSN status for when you run /playstation_status
/playstation_status -- The bot will fetch the PSN statuses of the set users and see if they're online.
"""

AGE = (humanize.naturaltime((datetime.datetime.now() - datetime.datetime(2021, 2, 8, 1, 1, 1)))).replace("", "ago")

ONLINE_EMOJI = u"\U0001F7E2"
AWAY_EMOJI = u"\U0001F7E1"
DO_NOT_DISTURB_EMOJI = u"\U000026D4"
OFFLINE_EMOJI = u"\U0001F534"
UNKNOWN_EMOJI = u"\U000026AB"
PENCIL_EMOJI = u"\U0000270F"
PLUS_EMOJI = u"\U00002795"
CROSS_EMOJI = u"\U0000274C"
LEFT_POINTING_EMOJI = u"\U0001F448"
RIGHT_POINTING_EMOJI = u"\U0001F449"
RAISED_HAND_EMOJI = u"\U0000270B"
CHECKMARK_EMOJI = u"\U00002705"
CANCELLED_EMOJI = u"\U0001F6AB"
NEXT_TRACK_EMOJI = u"\U000023ED"
CONTROLLER_EMOJI = u"\U0001F3AE"
UNLOCKED_EMOJI = u"\U0001F513"
LOCKED_EMOJI = u"\U0001F512"

ADMIN_LIST = [247340182]

BOT_URL = "https://t.me/GamersSocialManagerBot"
TOKEN = os.environ.get("GSM_TG_BOT_TOKEN")
XBOX_CLIENT_SECRET_EXPIRY_DATE = datetime.datetime.strptime(os.environ.get("XBOX_CLIENT_SECRET_EXPIRY_DATE", "Jun 16, 2024"), "%b %d, %Y").date()

