"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
import random
import humanize

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import constants
import requests
import datetime
import json

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


PORT = int(os.environ.get('PORT', '8443'))

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("*Drops down from a scaffolding* Hello there...")

def help_message(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(constants.help_message)

def quip(update, context):
    """Sends a quip everytime the command /quip is issued."""
    update.message.reply_text(random.choice(constants.quips))

def set_notify(update, context):
    f = open("notify.txt", "w")
    f.write(" ".join(context.args))
    f.close()
    update.message.reply_text("Done! A new notify message has been set.")
    

def notify(update, context):
    f = open("notify.txt", "r")
    update.message.reply_text(f.read())
    f.close()

def status(update, context):
    online_statuses = ""
    for friend in constants.FRIENDS_XUID:
        resp = requests.get("https://xapi.us/v2/{}/presence".format(
            constants.FRIENDS_XUID[friend]),
            headers={"X-AUTH":os.environ.get("XPAI_API_KEY")})
        if resp.status_code != 200:
            update.message.reply_text("Something went wrong with the API @ChakraAligningChadLad")
        resp = json.loads(resp.text)
        if resp["state"] == "Offline":
            online_statuses += f"{constants.OFFLINE_EMOJI} {friend}: {resp['state']}\nLast seen: "
            if resp.get("cloaked"):
                online_statuses += "Unknown\n\n"
            else:
                last_seen = humanize.naturaltime(datetime.datetime.fromisoformat(resp["lastSeen"]["timestamp"][:-5]) - datetime.datetime.utcnow())
                last_seen = last_seen.replace("from now", "ago")
                online_statuses += f"{last_seen}\n\n"
        else:
            online_statuses += f"{constants.ONLINE_EMOJI} {friend}: {resp['state']}\nPlaying: "
            if resp.get("cloaked"):
                online_statuses += "Unknown\n\n"
            else:
                online_statuses += f"{resp['devices'][0]['titles'][0]['name']}\n\n"
    update.message.reply_text(online_statuses)

# def echo(update, context):
#     """Echo the user message."""
#     update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = os.environ.get("CHADDICTS_TG_BOT_TOKEN")
    updater = Updater(
        TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_message))
    dp.add_handler(CommandHandler("quip", quip))
    dp.add_handler(CommandHandler("notify", notify))
    dp.add_handler(CommandHandler("set_notify", set_notify))
    dp.add_handler(CommandHandler("status", status))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    # updater.bot.set_webhook(url=settings.WEBHOOK_URL)
    updater.bot.set_webhook("https://chaddicts-tg-bot.herokuapp.com/" + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == '__main__':
    main()