"""
This is a bot made for the Telegram Messenger application. The purpose of this
bot is to connect gamers by allowing them to see other's online statuses, and
notifying each other when it's time to play.
"""
import handlers
import os

from argparse import ArgumentParser
from general.utils import import_root_dotenv_file
from external_handlers.apis_wrapper import ApisWrapper
from general.db import DBConnection
from general.values import TOKEN
from telegram.ext import (Updater, CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          PreCheckoutQueryHandler)


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
    dispatcher = updater.dispatcher
    # Register nonconversation handler commands
    register_nonconversation_commands(dispatcher)
    # Register the conversation handler commands
    register_conversation_commands(dispatcher)

    # If the bot's db is running locally, load dotenv environment variables
    if args.localdb:
        import_root_dotenv_file()

    # Set up the database singleton object
    DBConnection(DBConnection.authenticate_an_unauthenticated_db_url(
        os.getenv("GSM_DB_URL_WITHOUT_USERNAME_AND_PASSWORD"),
        os.getenv("GSM_DB_USERNAME"), os.getenv("GSM_DB_PASSWORD"),
        is_db_local=args.localdb
    ))

    # Start the Bot
    if args.localprod:
        updater.start_polling()
    else:
        # Setup the APIs if we are running the bot on prod.
        ApisWrapper()
        updater.start_webhook(listen="0.0.0.0", url_path=TOKEN,
                              webhook_url=f"https://gamersutilitybot.com/{TOKEN}")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def register_nonconversation_commands(dispatcher):
    # Register all non-conversation handlers, keeping them in the same group.
    ## Register the non-conversation basic command handlers
    dispatcher.add_handler(CommandHandler("about", handlers.basic.about), 0)
    dispatcher.add_handler(CommandHandler("f", handlers.basic.f), 0)
    dispatcher.add_handler(CommandHandler("mf", handlers.basic.mf), 0)
    dispatcher.add_handler(CommandHandler("wdhs", handlers.basic.wdhs), 0)
    dispatcher.add_handler(CommandHandler("age", handlers.basic.age), 0)
    dispatcher.add_handler(CommandHandler("donate", handlers.basic.donate), 0)
    dispatcher.add_handler(
        CallbackQueryHandler(
            handlers.basic.donate_using_telegram,
            pattern="^donate_using_telegram$"
        ), 0
    )
    # Pre-checkout handler to final check
    dispatcher.add_handler(PreCheckoutQueryHandler(
        handlers.basic.precheckout_callback
    ))
    dispatcher.add_handler(MessageHandler(
        Filters.successful_payment, handlers.basic.successful_payment_callback
    ))
    dispatcher.add_handler(
        CommandHandler("support", handlers.basic.support), 0
    )
    dispatcher.add_handler(
        CommandHandler("feedback", handlers.basic.feedback), 0
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.status_update.new_chat_members, handlers.basic.new_member
        )
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.status_update.left_chat_member, handlers.basic.left_member
        )
    )
    dispatcher.add_error_handler(handlers.basic.error) # log all errors

    ## Register the non-conversation notify group command handlers
    dispatcher.add_handler(
        CommandHandler(
            "list_notify_groups",
            handlers.notify_groups.utilities.list_notify_groups
        ), 0
    )
    dispatcher.add_handler(
        CommandHandler(
            "notify",
            handlers.notify_groups.utilities.notify
        ), 0
    )
    ## Register the non-conversation status group command handlers
    dispatcher.add_handler(
        CommandHandler(
            "status",
            handlers.status.display_status.status
        ), 0
    )


def register_conversation_commands(dispatcher):
    conversation_handlers = []
    conversation_handlers.append(ConversationHandler(
        entry_points=[
            CommandHandler("announce", handlers.basic.announce)
        ],
        states={
            handlers.basic.AWAITING_CONFIRMATION: [
                CallbackQueryHandler(
                    handlers.basic.confirm_announcement,
                    pattern="^confirm_announcement$"
                ),
                CallbackQueryHandler(
                    handlers.basic.cancel_announcement,
                    pattern="^cancel_announcement$"
                )
            ]
        },
        fallbacks=[
            MessageHandler(Filters.text, lambda u,c : None)
        ],
    ))
    conversation_handlers.append(ConversationHandler(
        entry_points=[
            CommandHandler("start", handlers.basic.start, pass_args=True),
            CommandHandler("help", handlers.basic.help_main_menu),
            CallbackQueryHandler(
                handlers.basic.help_main_menu,
                pattern="^help_main_menu$"
            )
        ],
        states={
            handlers.basic.HELP_MENU: [
                CallbackQueryHandler(
                    handlers.basic.help_general,
                    pattern="^general$"
                ),
                CallbackQueryHandler(
                    handlers.basic.help_notify_group_menu,
                    pattern="^notify_group_menu$"
                ),
                CallbackQueryHandler(
                    handlers.basic.help_add_notify_group,
                    pattern="^add_notify_group$"
                ),
                CallbackQueryHandler(
                    handlers.basic.help_modify_notify_group,
                    pattern="^modify_notify_group$"
                ),
                CallbackQueryHandler(
                    handlers.basic.help_invite_to_notify_group,
                    pattern="^invite_to_notify_group$"
                ),
                CallbackQueryHandler(
                    handlers.basic.help_list_notify_groups,
                    pattern="^list_notify_groups$"
                ),
                CallbackQueryHandler(
                    handlers.basic.help_notify,
                    pattern="^notify$"
                ),
                CallbackQueryHandler(
                    handlers.basic.help_status_user_menu,
                    pattern="^status_user_menu$"
                ),
                CallbackQueryHandler(
                    handlers.basic.help_add_status_user,
                    pattern="^add_status_user$"
                ),
                CallbackQueryHandler(
                    handlers.basic.help_modify_status_user,
                    pattern="^modify_status_user$"
                ),
                CallbackQueryHandler(
                    handlers.basic.help_status,
                    pattern="^status$"
                ),
            ]
        },
        fallbacks=[
            MessageHandler(Filters.text, lambda u,c : None)
        ],
        allow_reentry=True,
        per_user=False
    ))
    conversation_handlers.append(ConversationHandler(
        entry_points=[
            CommandHandler(
                "add_status_user", handlers.status.add_status_user.start
            ),
            CallbackQueryHandler(
                handlers.status.add_status_user.start,
                pattern="^asu_[-]?[0-9]+$"
            )
        ],
        states={
            handlers.status.add_status_user.TYPING_DISPLAY_NAME: [
                MessageHandler(
                    Filters.text & (~Filters.command),
                    handlers.status.add_status_user.process_display_name
                ),
            ],
            handlers.status.add_status_user.TYPING_XBOX_GAMERTAG: [
                MessageHandler(
                    Filters.text & (~Filters.command),
                    handlers.status.add_status_user.process_xbox_gamertag
                ),
                CallbackQueryHandler(
                    handlers.status.add_status_user.process_xbox_gamertag,
                    pattern="^skip_xbox_gamertag$"
                )
            ],
            handlers.status.add_status_user.TYPING_PSN_ONLINE_ID: [
                MessageHandler(
                    Filters.text & (~Filters.command),
                    handlers.status.add_status_user.process_psn_online_id
                ),
                CallbackQueryHandler(
                    handlers.status.add_status_user.process_psn_online_id,
                    pattern="^skip_psn_online_id$"
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(
                handlers.status.add_status_user.cancel,
                "^cancel$"
            ),
            MessageHandler(Filters.command, lambda u,c : handlers.common.cancel_current_conversation(u, c, "/add_status_user"))
        ],
        allow_reentry=True
    ))

    conversation_handlers.append(ConversationHandler(
        entry_points=[
            CommandHandler(
                "modify_status_user",
                handlers.status.modify_status_user.start
            ),
            CallbackQueryHandler(
                handlers.status.modify_status_user.start,
                pattern="^modify_status_user$"
            ),
            CallbackQueryHandler(
                handlers.status.modify_status_user.start,
                pattern="^msu_[-]?[0-9]+$"
            )
        ],
        states={
            handlers.status.modify_status_user.MAIN_MENU: [
                CallbackQueryHandler(
                    handlers.status.modify_status_user.start,
                    pattern="^modify_status_user$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.edit_or_delete,
                    pattern="^[0-9a-f]{24}$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.edit,
                    pattern="^edit_[0-9a-f]{24}$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.delete,
                    pattern="^delete_[0-9a-f]{24}$"
                ),
                # If we get any text or commands, we can just ignore it
                # MessageHandler(Filters.text | Filters.command,
                #                lambda u,c : handlers.status.MODIFYING_STATUS_USER)
            ],
            handlers.status.modify_status_user.EDITING_DISPLAY_NAME: [
                MessageHandler(
                    Filters.text & (~Filters.command),
                    handlers.status.modify_status_user.process_display_name
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.process_display_name,
                    pattern="^skip_display_name$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.cancel,
                    pattern="^cancel$"
                ),
            ],
            handlers.status.modify_status_user.EDITING_XBOX_GAMERTAG: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    handlers.status.modify_status_user.process_xbox_gamertag
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.process_xbox_gamertag,
                    pattern="^disconnect$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.process_xbox_gamertag,
                    pattern="^skip_xbox_gamertag$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.cancel,
                    pattern="^cancel$"
                ),

            ],
            handlers.status.modify_status_user.EDITING_PSN_ONLINE_ID: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    handlers.status.modify_status_user.process_psn_online_id
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.process_psn_online_id,
                    pattern="^disconnect$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.process_psn_online_id,
                    pattern="^skip_psn_online_id$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.cancel,
                    pattern="^cancel$"
                ),
            ],
            handlers.status.modify_status_user.DELETING_EMPTY_STATUS_USER: [
                CallbackQueryHandler(
                    handlers.status.modify_status_user.cancel,
                    pattern="^cancel$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.confirm_delete,
                    pattern="^confirm_delete_[0-9a-f]{24}$"
                ),
            ],
            handlers.status.modify_status_user.DELETING_STATUS_USER: [
                CallbackQueryHandler(
                    handlers.status.modify_status_user.edit_or_delete,
                    pattern="^[0-9a-f]{24}$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.delete,
                    pattern="^delete_[0-9a-f]{24}$"
                ),
                CallbackQueryHandler(
                    handlers.status.modify_status_user.confirm_delete,
                    pattern="^confirm_delete_[0-9a-f]{24}$"
                ),
            ]
        },
        fallbacks=[
            MessageHandler(Filters.text, lambda u,c : None)
        ],
        allow_reentry=True
    ))

    conversation_handlers.append(ConversationHandler(
        entry_points=[
            CommandHandler(
                "add_notify_group",
                handlers.notify_groups.creation.start
            ),
            CallbackQueryHandler(
                handlers.notify_groups.creation.start,
                pattern="^ang_[-]?[0-9]+$"
            )
        ],
        states={
            handlers.notify_groups.creation.TYPING_NAME: [
                MessageHandler(
                    Filters.text & (~Filters.command),
                    handlers.notify_groups.creation.process_name
                ),
                CallbackQueryHandler(
                    handlers.notify_groups.creation.process_name,
                    pattern="^.*$"
                )
            ],
            handlers.notify_groups.creation.TYPING_DESCRIPTION: [
                MessageHandler(
                    Filters.text & (~Filters.command),
                    handlers.notify_groups.creation.process_description
                ),
                CallbackQueryHandler(
                    handlers.notify_groups.creation.process_description,
                    pattern="^skip_description$"
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(handlers.notify_groups.creation.cancel,
                                 "^cancel$"),
            MessageHandler(Filters.command, lambda u,c : handlers.common.cancel_current_conversation(u, c, "/add_notify_group"))
        ],
        allow_reentry=True
    ))

    conversation_handlers.append(ConversationHandler(
        entry_points=[
            CommandHandler("modify_notify_group",
                           handlers.notify_groups.modification.start),
            CallbackQueryHandler(handlers.notify_groups.modification.start,
                                 pattern="^modify_notify_group$"),
            CallbackQueryHandler(
                handlers.notify_groups.modification.start,
                pattern="^mng_[-]?[0-9]+$"
            )
        ],
        states={
            handlers.notify_groups.modification.MAIN_MENU: [
                CallbackQueryHandler(handlers.notify_groups.modification.start,
                                        pattern="^modify_notify_group$"),
                CallbackQueryHandler(handlers.notify_groups.modification.edit_or_delete,
                                        pattern="^[0-9a-f]{24}$"),
                CallbackQueryHandler(handlers.notify_groups.modification.edit,
                                        pattern="^edit_[0-9a-f]{24}$"),
                CallbackQueryHandler(handlers.notify_groups.modification.delete,
                                        pattern="^delete_[0-9a-f]{24}$"),
                # If we get any text or commands, we can just ignore it
                # MessageHandler(Filters.text | Filters.command,
                #                lambda u,c : handlers.status.MODIFYING_STATUS_USER)
            ],
            handlers.notify_groups.modification.EDITING_NOTIFY_GROUP_NAME: [
                CallbackQueryHandler(
                    handlers.notify_groups.modification.cancel,
                    pattern="^cancel$"
                ),
                MessageHandler(
                    Filters.text & (~Filters.command),
                    handlers.notify_groups.modification.process_name
                ),
                CallbackQueryHandler(
                    handlers.notify_groups.modification.process_name,
                    pattern="^.*$"
                ),
            ],
            handlers.notify_groups.modification.EDITING_NOTIFY_GROUP_DESCRIPTION: [
                MessageHandler(
                    Filters.text & (~Filters.command),
                    handlers.notify_groups.modification.process_description
                ),
                CallbackQueryHandler(
                    handlers.notify_groups.modification.process_description,
                    pattern="^skip_description$"
                ),
                CallbackQueryHandler(
                    handlers.notify_groups.modification.cancel,
                    pattern="^cancel$"
                ),
            ],
            handlers.notify_groups.modification.EDITING_NOTIFY_GROUP_MEMBERS: [
                CallbackQueryHandler(
                    handlers.notify_groups.modification.cancel,
                    pattern="^cancel$"
                ),
                CallbackQueryHandler(
                    handlers.notify_groups.modification.process_members,
                ),
            ],
            handlers.notify_groups.modification.DELETING_NOTIFY_GROUP: [
                CallbackQueryHandler(
                    handlers.notify_groups.modification.edit_or_delete,
                    pattern="^[0-9a-f]{24}$"
                ),
                CallbackQueryHandler(
                    handlers.notify_groups.modification.delete,
                    pattern="^delete_[0-9a-f]{24}$"
                ),
                CallbackQueryHandler(
                    handlers.notify_groups.modification.confirm_delete,
                    pattern="^confirm_delete_[0-9a-f]{24}$"
                ),
            ]
        },
        fallbacks=[
            MessageHandler(Filters.text, lambda u,c : None)
        ],
        allow_reentry=True
    ))

    conversation_handlers.append(ConversationHandler(
        entry_points=[
            CommandHandler(
                "invite_to_notify_group",
                handlers.notify_groups.invitations.invite
            )
        ],
        states={
            handlers.notify_groups.invitations.WAITING_FOR_REPLY: [
                CallbackQueryHandler(
                    handlers.notify_groups.invitations.reply_to_invite,
                    pattern="^(accept|decline)_[0-9a-f]{24}_[0-9a-f]{24}$"
                ),
                CallbackQueryHandler(
                    handlers.notify_groups.invitations.revoke_invitation,
                    pattern="^revoke-invite_[0-9a-f]{24}_[0-9a-f]{24}$"
                ),
            ]
        },
        fallbacks=[
            CallbackQueryHandler(handlers.notify_groups.creation.cancel,
                                 "^cancel$"),
        ],
        allow_reentry=True,
        per_user=False,
    ))

    # Register all conversation handlers in different groups so that different
    # conversations can be started mid-conversation.
    for idx, conversation_handler in enumerate(conversation_handlers):
        dispatcher.add_handler(conversation_handler, idx+1)

    return conversation_handlers

if __name__ == '__main__':
    main()
