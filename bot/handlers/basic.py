import logging

from handlers.common import escape_text
from general import values
from telegram import ParseMode


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    start_msg = ("You've started me up\! Use /help to learn more about what "
                 f"I can do for you {values.SMILEY_EMOJI}")

    update.message.reply_animation(
        open(values.OBIWAN_HELLO_THERE_GIF_FILEPATH, "rb")
    )
    update.message.reply_text(start_msg, parse_mode=ParseMode.MARKDOWN_V2)


def about(update, context):
    bot_version_escaped_str = escape_text(values.BOT_VERSION.__str__())
    update.message.reply_text(
        f"Gamers Utility Bot v{bot_version_escaped_str}\n"
        "_Created by [Ahmed Siddiqui](https://github.com/AhmedNSidd/)_\n\n"
        "This is a Telegram bot created to give gamers some helpful utilities,"
        "making it easier to game with other users in group chats\. It does "
        "this through 2 main features:\n\n"
        f"{values.RIGHT_POINTING_EMOJI} The bot allows you to view the "
        "Online Status of gamers on Xbox Live & PSN through the Status Users "
        "feature\.\n"
        f"{values.RIGHT_POINTING_EMOJI} The bot allows you to create Notify "
        "Groups consisting of other members in a group chat\. You can use a "
        "Notify Group to notify those members when you want to play games "
        "with them, or to send them any other message\.",
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(values.help_message, parse_mode=ParseMode.MARKDOWN_V2)


def f(update, context):
    """Replies with a gif to pay respect."""
    update.message.reply_animation(
        open(values.F_TO_PAY_RESPECT_GIF_FILEPATH, "rb")
    )


def mf(update, context):
    """Replies with a sad.. sad voice note."""
    update.message.reply_audio(
        open(values.MISSION_FAILED_AUDIO_FILEPATH, "rb")
    )

def age(update, context):
    update.message.reply_text(
        "Didn't your mother ever teach you it's not polite to ask a bot its "
        f"age? Anyway, I am {values.AGE} {values.SMILEY_EMOJI}",
        parse_mode=ParseMode.MARKDOWN_V2
    )

def error(update, context):
    """Log Errors caused by Updates."""
    print('Update "%s" caused error "%s"', update, context.error)
    logger.warning('Update "%s" caused error "%s"', update, context.error)
