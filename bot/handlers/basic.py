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
    start_msg = ("\*Drops down from a scaffolding\* Hello there...\n\nChoose "
                 "the following options")
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
                              parse_mode=ParseMode.MARKDOWN)

def test(update, context):
    """Send a message when the command /help is issued."""
    print(update)
    print(update.message.chat.permissions)

def help_message(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(values.help_message)

def f(update, context):
    """Replies with a gif to pay respect."""
    update.message.reply_animation("https://thumbs.gfycat.com/SkeletalDependableAndeancat-size_restricted.gif")

def mf(update, context):
    """Replies with a sad.. sad voice note."""
    update.message.reply_audio("https://www.myinstants.com/media/sounds/mission-failed-well-get-em-next-time.mp3")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
