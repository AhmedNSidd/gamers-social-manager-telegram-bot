import logging

from general import values
from telegram import ParseMode, Message


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
        "Didn't your mother ever teach you it's not polite to ask a bot it's "
        f"age? Anyway, I am {values.AGE} {values.SMILEY_EMOJI}",
        parse_mode=ParseMode.MARKDOWN_V2
    )

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
