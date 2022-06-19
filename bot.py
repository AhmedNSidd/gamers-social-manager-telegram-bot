"""
This is a bot made for the Telegram Messenger application. The purpose of this
bot is to connect gamers by allowing them to see other's online statuses, and
notifying each other when it's time to play.
"""
from handlers import basic, notify, status
from general.production import PRODUCTION_READY, PORT
from general.values import HEROKU_APP_URL, TOKEN
from telegram.ext import Updater, CommandHandler
from scripts.db.instantiate_tables import instantiate_tables


def main():
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", basic.start))
    dp.add_handler(CommandHandler("help", basic.help_message))
    dp.add_handler(CommandHandler("f", basic.f))
    dp.add_handler(CommandHandler("mf", basic.mf))
    dp.add_handler(CommandHandler("add_notify_user", notify.add_notify_user))
    dp.add_handler(CommandHandler("del_notify_user", notify.del_notify_user))
    dp.add_handler(CommandHandler("set_notify_msg", notify.set_notify_msg))
    dp.add_handler(CommandHandler("list_notify_users", notify.list_notify_users))
    dp.add_handler(CommandHandler("list_notify_msg", notify.list_notify_msg))
    dp.add_handler(CommandHandler("notify", notify.notify))
    dp.add_handler(CommandHandler("add_xbox_status", status.add_xbox_status))
    dp.add_handler(CommandHandler("del_xbox_status", status.del_xbox_status))
    dp.add_handler(CommandHandler("list_xbox_status", status.list_xbox_status))
    dp.add_handler(CommandHandler("xbox_status", status.xbox_status, run_async=True))
    dp.add_handler(CommandHandler("add_playstation_status", status.add_playstation_status))
    dp.add_handler(CommandHandler("del_playstation_status", status.del_playstation_status))
    dp.add_handler(CommandHandler("list_playstation_status", status.list_playstation_status))
    dp.add_handler(CommandHandler("playstation_status", status.playstation_status))

    # log all errors
    dp.add_error_handler(basic.error)

    # Create all the necessary tables for the running of the bot.
    instantiate_tables()

    # Start the Bot
    if PRODUCTION_READY:
        updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=TOKEN,
                            webhook_url=f"{HEROKU_APP_URL}/{TOKEN}")
    else:
        updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == '__main__':
    main()
