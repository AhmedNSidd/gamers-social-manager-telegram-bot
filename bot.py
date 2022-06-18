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
from handlers import basic, notify, status
from general.production import PRODUCTION_READY, PORT
from general.values import HEROKU_APP_URL, TOKEN
from telegram.ext import Updater, CommandHandler
from scripts.db.instantiate_tables import instantiate_tables


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
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
    dp.add_handler(CommandHandler("xbox_status", status.xbox_status, run_async=True))
    dp.add_handler(CommandHandler("add_playstation_status_user", status.add_playstation_status_user))
    dp.add_handler(CommandHandler("del_playstation_status_user", status.del_playstation_status_user))
    dp.add_handler(CommandHandler("list_playstation_status_user", status.list_playstation_status_users))
    dp.add_handler(CommandHandler("playstation_status", status.playstation_status))

    # log all errors
    dp.add_error_handler(basic.error)

    # Create all the necessary tables for the running of the bot.
    instantiate_tables()

    # Start the Bot
    if PRODUCTION_READY:
        updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=TOKEN)
        updater.bot.set_webhook(f"{HEROKU_APP_URL}/{TOKEN}")
    else:
        updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == '__main__':
    main()
