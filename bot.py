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

import os
from handlers import basic, notify, status
from production import PRODUCTION_READY
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


PORT = int(os.environ.get('PORT', '8443'))

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
    dp.add_handler(CommandHandler("start", basic.start))
    dp.add_handler(CommandHandler("help", basic.help_message))
    dp.add_handler(CommandHandler("quip", basic.quip))
    dp.add_handler(CommandHandler("add_notify_user", notify.add_notify_user))
    dp.add_handler(CommandHandler("del_notify_user", notify.del_notify_user))
    dp.add_handler(CommandHandler("set_notify_msg", notify.set_notify_msg))
    dp.add_handler(CommandHandler("list_notify_users", notify.list_notify_users))
    dp.add_handler(CommandHandler("list_notify_msg", notify.list_notify_msg))
    dp.add_handler(CommandHandler("notify", notify.notify))
    dp.add_handler(CommandHandler("add_status_user", status.add_status_user))
    dp.add_handler(CommandHandler("del_status_user", status.del_status_user))
    dp.add_handler(CommandHandler("list_status_user", status.list_status_users))
    dp.add_handler(CommandHandler("status", status.status))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(basic.error)

    # Start the Bot
    if PRODUCTION_READY:
        updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=TOKEN)
        updater.bot.set_webhook("https://chaddicts-tg-bot.herokuapp.com/" + TOKEN)
    else:
        updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == '__main__':
    main()