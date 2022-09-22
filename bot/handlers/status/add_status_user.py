import asyncio

from aiohttp import ClientResponseError
from handlers.common import get_one_mention, escape_text
from external_handlers.apis_wrapper import ApisWrapper
from general import strings, values, inline_keyboards
from general.db import DBConnection
from handlers.status.common import stringify_status_user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler


# Conversation states for the CommandHandler for add_status_user
TYPING_DISPLAY_NAME, TYPING_XBOX_GAMERTAG, TYPING_PSN_ONLINE_ID = range(3)


def start(update, context):
    """
    Sends a private message to the user starting the add_status_user process
    and asking for their display name
    """
    # Check if the conversation was started through a button
    is_callback = False
    if update.callback_query:
        is_callback = True
        update = update.callback_query
        update.answer()
        context.user_data["user_id"] = update.message.chat.id
        callback_data_tokens = update.data.split("_")
        group_chat_id = callback_data_tokens[1]
        group_chat = context.bot.get_chat(group_chat_id)
        context.user_data["chat_id"] = group_chat.id
        context.user_data["group_name"] = group_chat.title
    else:
        context.user_data["user_id"] = update.message.from_user.id
        context.user_data["chat_id"] = update.message.chat.id
        context.user_data["group_name"] = (
            update.message.chat.title
            if context.user_data["chat_id"] != context.user_data["user_id"]
            else None
        )

    # TODO: Maybe consider adding this to the user data
    user_mention = get_one_mention(
        context.bot, context.user_data["user_id"], context.user_data["chat_id"]
    )

    # If the current conversation is happening in a group chat, send a button
    # to the user in a private chat which will add a status user to the group
    # chat, and end this conversation.
    if not is_callback and context.user_data["group_name"]:
        escaped_group_name = escape_text(context.user_data['group_name'])
        try:
            context.bot.send_message(
                context.user_data["user_id"],
                strings.CLICK_BUTTON_TO_START_PROCESS(
                    f"adding a status user for the _{escaped_group_name}_ "
                    "group chat"
                ),
                reply_markup=inline_keyboards.asu_start_keyboard(
                    context.user_data["chat_id"]
                ),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        except Unauthorized:
            # send a group message that the bot was unable to send a private
            # message if there's an error
            update.message.reply_text(
                strings.BOT_UNABLE_TO_SEND_PRIVATE_MESSAGE(
                    user_mention,
                    "adding a status user",
                    "add\_status\_user"
                ),
                reply_markup=inline_keyboards.go_to_private_chat_keyboard(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            # send a group message that the bot sent a private message to add
            # a status user
            update.message.reply_text(
                strings.BOT_SENT_A_PRIVATE_MESSAGE(
                    user_mention, "to add your status user for this group chat"
                ),
                reply_markup=inline_keyboards.go_to_private_chat_keyboard(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        finally:
            return ConversationHandler.END

    # Set up the status user that we want to add
    context.user_data["status_user"] = {
        "user_id": context.user_data["user_id"],
        "chat_id": context.user_data["chat_id"],
        "group_name": context.user_data["group_name"]
    }

    # Send the user prompt messages to start the process of adding a status
    # user

    context.user_data["messages_to_delete"] = []
    context.user_data["messages_to_delete"].append(
        update.message.reply_text(
            strings.ASU_INTRO(
                user_mention,
                escape_text(context.user_data["group_name"])
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_keyboards.cancel_keyboard()
        )
    )
    context.user_data["messages_to_delete"].append(
        update.message.reply_text(
            strings.ASU_ENTER_DISPLAY_NAME(
                escape_text(context.user_data["group_name"])
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_keyboards.cancel_keyboard()
        )
    )

    return TYPING_DISPLAY_NAME


def process_display_name(update, context):
    display_name = update.message.text.strip()
    chat_id = context.user_data.get("chat_id")
    context.user_data["messages_to_delete"].append(update.message)

    if not display_name:
        # If the display name is empty, then send an error message.
        context.user_data["messages_to_delete"].append(
            update.message.reply_text(
                strings.ASU_INVALID_DISPLAY_NAME(),
                reply_markup=inline_keyboards.cancel_keyboard(),
                parse_mode=ParseMode.MARKDOWN_V2,
                quote=True
            )
        )
        return TYPING_DISPLAY_NAME

    # Check if an existing display name is present in the group/private chat.
    users_with_the_same_name = DBConnection().count_documents(
        "statususers",
        {"chat_id": chat_id, "display_name": display_name}
    )
    if users_with_the_same_name > 0:
        context.user_data["messages_to_delete"].append(
            update.message.reply_text(
                strings.ASU_DUPLICATE_DISPLAY_NAME(
                    escape_text(context.user_data["group_name"])
                ),
                reply_markup=inline_keyboards.cancel_keyboard(),
                parse_mode=ParseMode.MARKDOWN_V2,
                quote=True
            )
        )
        return TYPING_DISPLAY_NAME

    # if we've gotten here, it means the display name is unique.
    context.user_data["status_user"]["display_name"] = display_name

    while len(context.user_data["messages_to_delete"]) > 1:
        old_message = context.user_data["messages_to_delete"].pop()
        old_message.delete()

    context.bot.send_message(
        context.user_data.get("user_id"),
        strings.ASU_DISPLAY_NAME_SUCCESS(display_name),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    context.user_data["messages_to_delete"].append(context.bot.send_message(
        context.user_data.get("user_id"),
        strings.ASU_XBOX_GAMERTAG_PROMPT(),
        reply_markup=inline_keyboards.asu_xbox_gamertag_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    ))
    return TYPING_XBOX_GAMERTAG


def process_xbox_gamertag(update, context):
    is_callback = False
    if update.callback_query:
        is_callback = True
        update = update.callback_query
        xbox_gamertag = update.data
        update.answer()

    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_xbox_gamertag"
        )
    ]]
    if not is_callback:
        context.user_data["messages_to_delete"].append(update.message)
        xbox_gamertag = update.message.text.strip()
        if not xbox_gamertag:
            context.user_data["messages_to_delete"].append(
                update.message.reply_text(
                    strings.ASU_INVALID_XBOX_GAMERTAG_ERROR(),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=inline_keyboards.asu_xbox_gamertag_keyboard(),
                    quote=True
                )
            )
            return TYPING_XBOX_GAMERTAG

    if is_callback and xbox_gamertag == "skip_xbox_gamertag":
        status_msg_prefix = f"Skipped Xbox Live setup\n\n"
        context.user_data["status_user"]["xbox_gamertag"] = None
    else:
        context.user_data["messages_to_delete"].append(update.message.reply_text(
            f"{values.RAISED_HAND_EMOJI} Please hold as we process your Xbox "
            "Gamertag\. This might take around 10 seconds",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        ))
        try:
            context.user_data["status_user"]["xbox_account_id"] = asyncio.run(
                ApisWrapper().get_account_id_from_gamertag(xbox_gamertag)
            )
        except ClientResponseError as cre:
            if cre.status == 404:
                context.user_data["messages_to_delete"][-1].edit_text(
                    "The Xbox Gamertag you entered could not be found\! "
                    "Please enter a valid Xbox Gamertag",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                return TYPING_XBOX_GAMERTAG

        context.user_data["status_user"]["xbox_gamertag"] = xbox_gamertag
        status_msg_prefix = ("Great\! Your Xbox Gamertag has been set as "
                             f"`{xbox_gamertag}`\n\n")

    while len(context.user_data["messages_to_delete"]) > 1:
        old_message = context.user_data["messages_to_delete"].pop()
        old_message.delete()

    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_psn_online_id"
        )
    ]]
    context.bot.send_message(
        context.user_data.get("user_id"),
        status_msg_prefix,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    context.user_data["messages_to_delete"].append(context.bot.send_message(
        context.user_data.get("user_id"),
        "Now enter your PSN Online ID display your PSN "
        "status",
        reply_markup=InlineKeyboardMarkup(keyboard)
    ))
    return TYPING_PSN_ONLINE_ID


def process_psn_online_id(update, context):
    is_callback = False
    if update.callback_query:
        is_callback = True
        update = update.callback_query
        username = update.from_user['username']
        psn_online_id = update.data
        update.answer()

    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_psn_online_id"
        )
    ]]

    if not is_callback:
        username = update.message.from_user['username']
        context.user_data["messages_to_delete"].append(update.message)
        psn_online_id = update.message.text.strip()
        if not psn_online_id:
            keyboard = [[
                InlineKeyboardButton(
                    f"{values.CANCELLED_EMOJI} CANCEL",
                    callback_data=f"cancel"
                ),
                InlineKeyboardButton(
                    f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
                    callback_data=f"skip_psn_online_id"
                )
            ]]
            context.user_data["messages_to_delete"].append(update.message.reply_text(
                "You did not provide a valid PSN Online ID\.  Please enter a "
                "valid PSN Online ID",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return TYPING_PSN_ONLINE_ID

    if is_callback and psn_online_id == "skip_psn_online_id":
        status_msg_prefix = "Skipped PSN setup\n\n"
        context.user_data["status_user"]["psn_online_id"] = None
        context.user_data["status_user"]["psn_account_id"] = None
    else:
        context.user_data["messages_to_delete"].append(update.message.reply_text(
            f"{values.RAISED_HAND_EMOJI} Please hold as we process your PSN "
            "Online ID\. This might take around 5 seconds",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        ))
        try:
            context.user_data["status_user"]["psn_account_id"] = asyncio.run(
                ApisWrapper().get_account_id_from_online_id(psn_online_id)
            )
        except ClientResponseError as cre:
            if cre.status == 404:
                context.user_data["messages_to_delete"][-1].edit_text(
                    "The PSN Online ID you entered could not be found\! "
                    "Please enter a valid PSN Online ID",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                return TYPING_PSN_ONLINE_ID

        context.user_data["status_user"]["psn_online_id"] = psn_online_id
        status_msg_prefix = ("Great\! Your PSN Online ID has been set as "
                             f"`{psn_online_id}`\n\n")

    while len(context.user_data["messages_to_delete"]) > 1:
        old_message = context.user_data["messages_to_delete"].pop()
        old_message.delete()

    ret = process_new_status_user(context)
    if type(ret) == int:
        return ret
    
    del context.user_data["messages_to_delete"]

    if context.user_data.get("group_name"):
        mention = get_one_mention(
            context.bot,
            context.user_data['user_id'],
            context.user_data["chat_id"]
        )
        context.bot.send_message(
            context.user_data.get("chat_id"),
            f"`{context.user_data['status_user']['display_name']}` has been "
            f"added to the /status command by {mention}",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    context.bot.send_message(
        context.user_data["user_id"],
        status_msg_prefix,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    context.bot.send_message(
        context.user_data["user_id"],
        f"*You've successfully added a new status user\.* Below are the "
        "details of your new status user:\n\n" +
        stringify_status_user(context.bot, context.user_data["status_user"]),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    context.user_data.clear()
    return ConversationHandler.END


def process_new_status_user(context):
    if (not context.user_data["status_user"]["xbox_gamertag"] and
        not context.user_data["status_user"]["psn_online_id"]):
        keyboard = [[
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} CANCEL",
                callback_data=f"cancel"
            ),
            InlineKeyboardButton(
                f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
                callback_data=f"skip_xbox_gamertag"
            )
        ]]
        context.user_data["messages_to_delete"].append(context.bot.send_message(
            context.user_data.get("user_id"),
            "Sorry\! You can not add a status user with no gaming IDs\. We "
            "will ask you for your gaming IDs again\. Please enter at least "
            "one, or choose to cancel this process\n\nNow enter your *Xbox "
            "Gamertag*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2
        ))
        return TYPING_XBOX_GAMERTAG

    DBConnection().insert_one(
        "statususers",
        context.user_data["status_user"]
    )


def cancel(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    while context.user_data["messages_to_delete"]:
        old_message = context.user_data["messages_to_delete"].pop()
        old_message.delete()

    context.bot.send_message(
        context.user_data["user_id"],
        f"{values.CANCELLED_EMOJI} Cancelled the process of adding a status "
        "user"
    )
    context.user_data.clear()
    return ConversationHandler.END
