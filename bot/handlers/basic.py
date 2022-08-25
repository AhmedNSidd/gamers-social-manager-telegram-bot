import logging

from general import values
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    start_msg = ("**Drops down from a scaffolding** Hello there\.\.\.\n\n"
                 "Choose the following options")
    keyboard_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"{values.PLUS_EMOJI} Add a Status User",
                    callback_data="add_status_user"
                ),
                InlineKeyboardButton(
                    f"{values.PENCIL_EMOJI} Modify Status Users",
                    callback_data="modify_status_user"
                )
            ]
        ]
    )
    update.message.reply_text(start_msg, reply_markup=keyboard_markup,
                              parse_mode=ParseMode.MARKDOWN_V2)


def help_message(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(values.help_message, parse_mode=ParseMode.MARKDOWN_V2)


def f(update, context):
    """Replies with a gif to pay respect."""
    update.message.reply_animation(
        "https://thumbs.gfycat.com/SkeletalDependableAndeancat-size_restricted.gif"
    )


def mf(update, context):
    """Replies with a sad.. sad voice note."""
    update.message.reply_audio(
        "https://www.myinstants.com/media/sounds/mission-failed-well-get-em-next-time.mp3"
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
