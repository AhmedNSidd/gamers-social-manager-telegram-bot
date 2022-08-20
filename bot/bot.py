"""
This is a bot made for the Telegram Messenger application. The purpose of this
bot is to connect gamers by allowing them to see other's online statuses, and
notifying each other when it's time to play.
"""
import os

from argparse import ArgumentParser
from general.utils import import_root_dotenv_file
from external_handlers.apis_wrapper import ApisWrapper
from general.db import DBConnection
from general.values import TOKEN
from handlers import basic, notify_groups, status
from telegram.ext import (Updater, CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler)


def main():
    # Set up arguments to the program
    parser = ArgumentParser(description="Runs the GSM Telegram Bot")
    parser.add_argument(
        "--localdb",
        help="Indicates whether the database of the bot is running on localhost or not",
        action="store_true"
    )
    parser.add_argument(
        "--localprod",
        help="Indicates whether the bot should poll in order to get telegram updates",
        action="store_true"
    )
    args = parser.parse_args()

    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # Set up the Conversation Handlers
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
                                     pattern="^[0-9a-f]{24}$"),
                CallbackQueryHandler(status.modify_status_user.edit,
                                     pattern="^edit_[0-9a-f]{24}$"),
                CallbackQueryHandler(status.modify_status_user.delete,
                                     pattern="^delete_[0-9a-f]{24}$"),
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
                                     pattern="^confirm_delete_[0-9a-f]{24}$"),
            ],
            status.modify_status_user.DELETING_STATUS_USER: [
                CallbackQueryHandler(status.modify_status_user.edit_or_delete,
                                     pattern="^[0-9a-f]{24}$"),
                CallbackQueryHandler(status.modify_status_user.delete,
                                     pattern="^delete_[0-9a-f]{24}$"),
                CallbackQueryHandler(status.modify_status_user.confirm_delete,
                                     pattern="^confirm_delete_[0-9a-f]{24}$"),
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
            CommandHandler("add_notify_group", notify_groups.creation_and_modification.start)
        ],
        states={
            notify_groups.creation_and_modification.TYPING_NAME: [
                MessageHandler(Filters.text & (~Filters.command),
                               notify_groups.creation_and_modification.process_name),
            ],
            notify_groups.creation_and_modification.TYPING_DESCRIPTION: [
                MessageHandler(Filters.text & (~Filters.command),
                               notify_groups.creation_and_modification.process_description),
                CallbackQueryHandler(
                    notify_groups.creation_and_modification.process_description,
                    pattern="^skip_description$"
                )
            ],
            notify_groups.creation_and_modification.CHOOSING_JOINING_POLICY: [
                CallbackQueryHandler(
                    notify_groups.creation_and_modification.process_joining_policy,
                    pattern="^(open|inviteonly)_joining_policy$"
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(notify_groups.creation_and_modification.cancel, "^cancel$"),
            MessageHandler(Filters.command, notify_groups.creation_and_modification.stop_cmds)
        ],
        allow_reentry=True,
        per_chat=False,
        run_async=True
    )

    notify_group_invites_conversation = ConversationHandler(
        entry_points=[
            CommandHandler(
                "invite_to_notify_group",
                notify_groups.invitations.invite
            )
        ],
        states={
            notify_groups.invitations.WAITING_FOR_REPLY: [
                CallbackQueryHandler(
                    notify_groups.invitations.reply_to_invite,
                    pattern="^(accept|decline)_[0-9a-f]{24}$"
                )
            ]
        },
        fallbacks=[
            CallbackQueryHandler(notify_groups.creation_and_modification.cancel, "^cancel$"),
            MessageHandler(Filters.command, notify_groups.creation_and_modification.stop_cmds)
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

    dp.add_handler(add_notify_group_conversation, 4)
    dp.add_handler(notify_group_invites_conversation, 5)
    dp.add_handler(
        CommandHandler("list_notify_groups", notify_groups.utilities.list_notify_groups), 1
    )
    dp.add_handler(
        CommandHandler("join_notify_group", notify_groups.invitations.join), 1
    )

    dp.add_handler(add_status_user_conversation, 2)
    dp.add_handler(modify_status_user_conversation, 3)
    dp.add_handler(CommandHandler("status", status.display_status.status), 1)

    # log all errors
    dp.add_error_handler(basic.error)

     # If the bot's db is running locally, load dotenv environment variables
    if args.localdb:
        import_root_dotenv_file()

    # Set up the database singleton object
    DBConnection(DBConnection.authenticate_an_unauthenticated_db_url(
        os.getenv("GSM_DB_URL_WITHOUT_USERNAME_AND_PASSWORD"),
        os.getenv("GSM_DB_USERNAME"), os.getenv("GSM_DB_PASSWORD"),
        is_db_local=args.localdb
    ))

    # Setup the APIs
    ApisWrapper()

    # Start the Bot
    if args.localprod:
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0", url_path=TOKEN,
                              webhook_url=f"https://gamersutilitybot.com/{TOKEN}")
    #                         #   webhook_url=f"{HEROKU_APP_URL}/{TOKEN}")        

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == '__main__':
    main()
