import datetime
import humanize
import os

from semantic_version import Version


BOT_VERSION = Version("1.0.0")

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
    "The only thing falling faster than the GME stock are your grades"
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
LEDGER_EMOJI = u"\U0001F4D2"
WINK_EMOJI = u"\U0001F609"
ZANY_EMOJI = u"\U0001F92A"
MONEY_BAG_EMOJI = u"\U0001F4B0"
QUESTION_MARK_EMOJI = u"\U00002753"


ADMIN_LIST = [247340182]

TOKEN = os.environ.get("GUB_BOT_TOKEN")
PAYMENT_TOKEN = os.environ.get("GUB_PAYMENT_TOKEN")
FEEDBACK_TOKEN = os.environ.get("GUB_FEEDBACK_TOKEN")
XBOX_CLIENT_SECRET_EXPIRY_DATE = datetime.datetime.strptime("Jun 16, 2024", "%b %d, %Y").date()

OBIWAN_HELLO_THERE_GIF_FILEPATH = "media/obiwans-hello-there.mp4"
F_TO_PAY_RESPECT_GIF_FILEPATH = "media/f-to-pay-respect.gif"
MISSION_FAILED_AUDIO_FILEPATH = "media/mission-failed.mp3"
WHAT_DID_HE_SAY_VIDEO_FILEPATH = "media/what-did-he-say.mp4"