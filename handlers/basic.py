import random
import logging
from general import values

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("*Drops down from a scaffolding* Hello there...")

def help_message(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(values.help_message)

def quip(update, context):
    """Sends a quip everytime the command /quip is issued."""
    update.message.reply_text(random.choice(values.quips))

def get_group_id(update, context):
    """Replies with a group's chat ID"""
    update.message.reply_text(str(update.effective_chat.id))

# def echo(update, context):
#     """Echo the user message."""
#     update.message.reply_text(update.message.text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
