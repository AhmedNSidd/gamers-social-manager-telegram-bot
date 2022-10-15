import datetime
import humanize
import os

from semantic_version import Version


BOT_VERSION = Version("1.0.0")


help_message = """Here are the list of commands available to you:

General Commands
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-
/start \-\- Starts the bot up\.
/about \-\- Tells you a bit about the bot\.
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

disses = [
    "I'mmmmmmmmmmm sooorrryyyyyyyyy for your loss",
    "It looks like your face caught on fire and someone tried to put it out with a fork",
    "Why don't you go play a game that is better suited for your skills like ludo",
    "Your gene pool could use a little chlorine",
    "Why play so hard to get when you're already so hard to want",
    "I could get on your level but I don't like being on my knees as much as you do",
    "If you ran like your mouth you'd be in really good shape",
    "What's the difference between you and eggs? Eggs get laid and you don't",
    "To be fair, you do have to have a very high IQ to meditate",
    "The only thing falling faster than the GME stock are your grades",
    "I don't watch tiktok. I'm not a virgin"
]

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
MINUS_EMOJI = u"\U00002796"
USER_EMOJI = u"\U0001F464"
STAR_EMOJI = u"\U00002B50"
BELL_EMOJI = u"\U0001F514"
ENVELOPE_EMOJI = u"\U00002709"
INFORMATION_DESK_PERSON_EMOJI = u"\U0001F481"
NOTEPAD_EMOJI = u"\U0001F5D2"

ADMIN_LIST = [247340182]

TOKEN = os.environ.get("GUB_BOT_TOKEN")
XBOX_CLIENT_SECRET_EXPIRY_DATE = datetime.datetime.strptime("Jun 16, 2024", "%b %d, %Y").date()

OBIWAN_HELLO_THERE_GIF_FILEPATH = "media/obiwans-hello-there.mp4"
F_TO_PAY_RESPECT_GIF_FILEPATH = "media/f-to-pay-respect.gif"
MISSION_FAILED_AUDIO_FILEPATH = "media/mission-failed.mp3"