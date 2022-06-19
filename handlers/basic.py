import logging
from general import values


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("*Drops down from a scaffolding* Hello there...")

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
