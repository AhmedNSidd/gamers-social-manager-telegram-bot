"""
This is a bot made for the Telegram Messenger application. The purpose of this
bot is to connect gamers by allowing them to see other's online statuses, and
notifying each other when it's time to play.
"""
from external_handlers.apis_wrapper import ApisWrapper
from general.db import DBConnection
from general.production import PRODUCTION_READY, PORT
from general.values import HEROKU_APP_URL, TOKEN
from handlers import basic, notify, status
from scripts.db.instantiate_tables import instantiate_tables
from telegram.ext import (Updater, CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    add_status_user_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("add_status_user", status.add_status_user.start),
            CallbackQueryHandler(status.add_status_user.start,
                                 pattern="^add_status_user$")
        ],
        states={
            status.add_status_user.TYPING_DISPLAY_NAME: [
                MessageHandler(Filters.text & (~Filters.command),
                               status.add_status_user.process_display_name),
            ],
            status.add_status_user.TYPING_XBOX_GAMERTAG: [
                MessageHandler(Filters.text & (~Filters.command),
                               status.add_status_user.process_xbox_gamertag),
                CallbackQueryHandler(
                    status.add_status_user.process_xbox_gamertag,
                    pattern="^skip_xbox_gamertag$"
                )
            ],
            status.add_status_user.TYPING_PSN_ONLINE_ID: [
                MessageHandler(Filters.text & (~Filters.command),
                               status.add_status_user.process_psn_online_id),
                CallbackQueryHandler(
                    status.add_status_user.process_psn_online_id,
                    pattern="^skip_psn_online_id$"
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(status.add_status_user.cancel, "^cancel$"),
            MessageHandler(Filters.command, status.add_status_user.stop_cmds)
        ],
        allow_reentry=True,
        per_chat=False,
        run_async=True
    )

    modify_status_user_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("modify_status_user",
                           status.modify_status_user.start),
            CallbackQueryHandler(status.modify_status_user.start,
                                 pattern="^modify_status_user$"),
        ],
        states={
            status.modify_status_user.MAIN_MENU: [
                CallbackQueryHandler(status.modify_status_user.start,
                                     pattern="^modify_status_user$"),
                CallbackQueryHandler(status.modify_status_user.edit_or_delete,
                                     pattern="^[0-9]+$"),
                CallbackQueryHandler(status.modify_status_user.edit,
                                     pattern="^edit_[0-9]+$"),
                CallbackQueryHandler(status.modify_status_user.delete,
                                     pattern="^delete_[0-9]+$"),
                # If we get any text or commands, we can just ignore it
                # MessageHandler(Filters.text | Filters.command,
                #                lambda u,c : status.MODIFYING_STATUS_USER)
            ],
            status.modify_status_user.EDITING_DISPLAY_NAME: [
                MessageHandler(
                    Filters.text & (~Filters.command),
                    status.modify_status_user.process_display_name
                ),
                CallbackQueryHandler(
                    status.modify_status_user.process_display_name,
                    pattern="^skip_display_name$"
                ),
                CallbackQueryHandler(
                    status.modify_status_user.cancel,
                    pattern="^cancel$"
                ),
            ],
            status.modify_status_user.EDITING_XBOX_GAMERTAG: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    status.modify_status_user.process_xbox_gamertag
                ),
                CallbackQueryHandler(
                    status.modify_status_user.process_xbox_gamertag,
                    pattern="^disconnect$"
                ),
                CallbackQueryHandler(
                    status.modify_status_user.process_xbox_gamertag,
                    pattern="^skip_xbox_gamertag$"
                ),
                CallbackQueryHandler(
                    status.modify_status_user.cancel,
                    pattern="^cancel$"
                ),

            ],
            status.modify_status_user.EDITING_PSN_ONLINE_ID: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    status.modify_status_user.process_psn_online_id
                ),
                CallbackQueryHandler(
                    status.modify_status_user.process_psn_online_id,
                    pattern="^disconnect$"
                ),
                CallbackQueryHandler(
                    status.modify_status_user.process_psn_online_id,
                    pattern="^skip_psn_online_id$"
                ),
                CallbackQueryHandler(
                    status.modify_status_user.cancel,
                    pattern="^cancel$"
                ),
            ],
            status.modify_status_user.DELETING_EMPTY_STATUS_USER: [
                CallbackQueryHandler(status.modify_status_user.cancel,
                                     pattern="^cancel$"),
                CallbackQueryHandler(status.modify_status_user.confirm_delete,
                                     pattern="^confirm_delete_[0-9]+$"),
            ],
            status.modify_status_user.DELETING_STATUS_USER: [
                CallbackQueryHandler(status.modify_status_user.edit_or_delete,
                                     pattern="^[0-9]+$"),
                CallbackQueryHandler(status.modify_status_user.delete,
                                     pattern="^delete_[0-9]+$"),
                CallbackQueryHandler(status.modify_status_user.confirm_delete,
                                     pattern="^confirm_delete_[0-9]+$"),
            ]
        },
        fallbacks=[
            MessageHandler(Filters.text, lambda u,c : None)
        ],
        allow_reentry=True,
        per_chat=False,
        run_async=True
    )

    add_notify_group_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("add_notify_group", notify.add_notify_group.start)
        ],
        states={
            notify.add_notify_group.TYPING_NAME: [
                MessageHandler(Filters.text & (~Filters.command),
                               notify.add_notify_group.process_name),
            ],
            notify.add_notify_group.TYPING_DESCRIPTION: [
                MessageHandler(Filters.text & (~Filters.command),
                               notify.add_notify_group.process_description),
                CallbackQueryHandler(
                    notify.add_notify_group.process_description,
                    pattern="^skip_description$"
                )
            ],
            notify.add_notify_group.CHOOSING_JOINING_POLICY: [
                CallbackQueryHandler(
                    notify.add_notify_group.process_joining_policy,
                    pattern="^(Open|InviteOnly)_joining_policy$"
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(notify.add_notify_group.cancel, "^cancel$"),
            MessageHandler(Filters.command, notify.add_notify_group.stop_cmds)
        ],
        allow_reentry=True,
        per_chat=False,
        run_async=True
    )

    notify_group_invites_conversation = ConversationHandler(
        entry_points=[
            CommandHandler(
                "invite_to_notify_group",
                notify.notify_group_invites.invite
            )
        ],
        states={
            notify.notify_group_invites.WAITING_FOR_REPLY: [
                CallbackQueryHandler(
                    notify.notify_group_invites.reply_to_invite,
                    pattern="^(accept|decline)_[0-9]+$"
                )
            ]
        },
        fallbacks=[
            CallbackQueryHandler(notify.add_notify_group.cancel, "^cancel$"),
            MessageHandler(Filters.command, notify.add_notify_group.stop_cmds)
        ],
        allow_reentry=True,
        per_user=False,
        run_async=True
    )


    

    # Register handlers for commands. Also add an integer as the second
    # parameter to signify groupings.
    dp.add_handler(CommandHandler("start", basic.start), 1)
    dp.add_handler(CommandHandler("help", basic.help_message), 1)
    dp.add_handler(CommandHandler("f", basic.f), 1)
    dp.add_handler(CommandHandler("mf", basic.mf), 1)
    dp.add_handler(CommandHandler("test", basic.test), 1)

    # dp.add_handler(CommandHandler("add_notify_user", notify.add_notify_user))
    # dp.add_handler(CommandHandler("del_notify_user", notify.del_notify_user))
    # dp.add_handler(CommandHandler("set_notify_msg", notify.set_notify_msg))
    # dp.add_handler(CommandHandler("list_notify_users", notify.list_notify_users))
    # dp.add_handler(CommandHandler("list_notify_msg", notify.list_notify_msg))
    # dp.add_handler(CommandHandler("notify", notify.notify))
    dp.add_handler(add_notify_group_conversation, 4)
    dp.add_handler(notify_group_invites_conversation, 5)
    dp.add_handler(
        CommandHandler("list_notify_groups", notify.list_notify_groups.list), 1
    )
    dp.add_handler(
        CommandHandler("join_notify_group", notify.join_notify_group.join), 1
    )

    dp.add_handler(add_status_user_conversation, 2)
    dp.add_handler(modify_status_user_conversation, 3)
    dp.add_handler(CommandHandler("status", status.display_status.status), 1)

    # log all errors
    dp.add_error_handler(basic.error)

    # Setup necessary stuff for the running of the bot such as:
    # The database schema
    instantiate_tables()
    # Setup the APIs
    ApisWrapper()
    # Setup the connection to the database...
    DBConnection()

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
