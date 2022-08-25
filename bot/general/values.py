import datetime
import humanize
import os


help_message = """Here are the list of commands available to you:

General Commands
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-
/help \-\- The bot will send this message that you're reading right now\.
/quip \-\- The bot will hit you up with a mighty fine quip or just an okay one\.
/f \-\- The bot will reply with a gif to help pay respect\.
/mf \-\- The bot will reply with a sad\.\.\. sad\.\. voice note\.
/age \-\- The bot will reply with how old the bot is\.

Notify Group Commands \- Send a message while tagging preset users \(Meant to be used in group chats\)
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-
/add\_notify\_group \-\- create a notify group for that group chat
/modify\_notify\_group \-\- modify any of your notify groups for a specific group chat
`/invite\_to\_notify\_group example\_group\_name @example\_username1 @example\_username2` \-\- Invites the tagged users to your notify group
/list\_notify\_groups \-\- Lists all the notify groups in a group chat
`/notify example\_group\_name optional\_message` \-\- Notifies all members within a notify group with an optional message

Status Commands \- Get status of players on Xbox Live and PSN\.
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-
/add\_status\_user \-\- Create a status user belonging to a group chat or private chat
/modify\_status\_user \-\- Modify a status user belonging to a group chat or private chat
/status \-\- Lists the status of all status users within a group chat or private chat
"""

AGE = (humanize.naturaltime((datetime.datetime.now() - datetime.datetime(2021, 2, 8, 1, 1, 1)))).replace("ago", "old")

SMILEY_EMOJI = u"\U0001F60A"
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

BOT_USERNAME = "GamersSocialManagerBot"
BOT_URL = "https://t.me/GamersSocialManagerBot"
TOKEN = os.environ.get("GSM_TG_BOT_TOKEN")
XBOX_CLIENT_SECRET_EXPIRY_DATE = datetime.datetime.strptime("Jun 16, 2024", "%b %d, %Y").date()

