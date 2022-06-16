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

from handlers import basic, notify, status, credentials
from handlers.credentials import TYPING_CLIENT_ID, TYPING_CLIENT_SECRET, TYPING_NPSSO
from general.production import PRODUCTION_READY
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler
from telegram.ext.filters import Filters
from db.instantiate_tables import instantiate_tables


PORT = int(os.environ.get('PORT', '8443'))

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = os.environ.get("CHADDICTS_TG_BOT_TOKEN")
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", basic.start))
    dp.add_handler(CommandHandler("help", basic.help_message))
    dp.add_handler(CommandHandler("quip", basic.quip))
    dp.add_handler(CommandHandler("f", basic.f))
    dp.add_handler(CommandHandler("mf", basic.mf))
    dp.add_handler(CommandHandler("get_group_id", basic.get_group_id))
    dp.add_handler(CommandHandler("add_notify_user", notify.add_notify_user))
    dp.add_handler(CommandHandler("del_notify_user", notify.del_notify_user))
    dp.add_handler(CommandHandler("set_notify_msg", notify.set_notify_msg))
    dp.add_handler(CommandHandler("list_notify_users", notify.list_notify_users))
    dp.add_handler(CommandHandler("list_notify_msg", notify.list_notify_msg))
    dp.add_handler(CommandHandler("notify", notify.notify))
    dp.add_handler(CommandHandler("add_xbox_status_user", status.add_xbox_status_user))
    dp.add_handler(CommandHandler("del_xbox_status_user", status.del_xbox_status_user))
    dp.add_handler(CommandHandler("list_xbox_status_user", status.list_xbox_status_users))
    dp.add_handler(CommandHandler("xbox_status", status.xbox_status))
    dp.add_handler(CommandHandler("add_playstation_status_user", status.add_playstation_status_user))
    dp.add_handler(CommandHandler("del_playstation_status_user", status.del_playstation_status_user))
    dp.add_handler(CommandHandler("list_playstation_status_user", status.list_playstation_status_users))
    dp.add_handler(CommandHandler("playstation_status", status.playstation_status))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler("xbox_credentials_setup", credentials.xbox_credentials_setup)],
        states={
            TYPING_CLIENT_ID: [
                MessageHandler(Filters.text & (~Filters.command), credentials.store_xbox_client_id)
            ],
            TYPING_CLIENT_SECRET: [
                MessageHandler(Filters.text & (~Filters.command), credentials.store_xbox_client_secret)
            ]
        },
        fallbacks=[MessageHandler(Filters.command, credentials.cancel)],
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler("playstation_credentials_setup", credentials.playstation_credentials_setup)],
        states={
            TYPING_NPSSO: [
                MessageHandler(Filters.text & (~Filters.command), credentials.store_playstation_npsso)
            ]
        },
        fallbacks=[MessageHandler(Filters.command, credentials.cancel)],
    ))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(basic.error)

    # Create all the necessary tables for the running of the bot.
    instantiate_tables()

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
