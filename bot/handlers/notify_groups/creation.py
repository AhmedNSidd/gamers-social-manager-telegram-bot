from handlers.notify_groups.common import stringify_notify_group
from handlers.common import get_one_mention, send_loud_and_silent_message
from general import values
from general.db import DBConnection
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler
from telegram.error import Unauthorized


# Conversation states for the CommandHandler for add_status_user
TYPING_NAME, TYPING_DESCRIPTION = range(2)


def start(update, context):
    """
    Sends a private message to the user starting the add_notify_group process
    and asking for the group name
    """
    context.user_data["user_id"] = update.message.from_user.id
    context.user_data["chat_id"] = update.message.chat.id
    context.user_data["group_name"] = (
        update.message.chat.title
        if context.user_data["chat_id"] != context.user_data["user_id"]
        else None
    )
    if not context.user_data["group_name"]:
        update.message.reply_text(
            "You can only run this command in a group",
            quote=True
        )
        return ConversationHandler.END

    context.user_data["messages_to_delete"] = []
    context.user_data["notify_group_to_add"] = {
        "chat_id": context.user_data["chat_id"],
        "creator_id": context.user_data["user_id"]
    }
    user_mention = get_one_mention(
        context.bot, context.user_data["user_id"], context.user_data["chat_id"]
    )
    try:
        keyboard = [[
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} CANCEL",
                callback_data=f"cancel"
            ),
        ]]
        context.user_data["messages_to_delete"].append(
            context.bot.send_message(
                context.user_data["user_id"],
                f"Hey {update.message.from_user.first_name}\!\n\nWe will add "
                f"a notify group to the _{context.user_data['group_name']}_ "
                "group\.\n\nI will ask you for the name and description for "
                "this group\.\n\nYou can choose to cancel the process of "
                "adding this notify group at any point during this process",
                parse_mode=ParseMode.MARKDOWN_V2
            )
        )
        context.user_data["messages_to_delete"].append(
            context.bot.send_message(
                context.user_data["user_id"],
                "Enter the *name* for the notify group you want to add to the "
                f"_{context.user_data['group_name']}_ group  e\.g\. "
                "_Weeknight\_Gamers_\n\n*Note* The name can NOT include "
                "spaces",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        )
    except Unauthorized:
        # send a group message that the bot was unable to send a private message
        keyboard = [[
            InlineKeyboardButton(
                f"{values.RIGHT_POINTING_EMOJI} GO TO PRIVATE CHAT",
                url=f"{values.BOT_URL}"
            ),
        ]]
        update.message.reply_text(
            f"Hey {user_mention}\!\n\nThe bot was unable to send you a "
            "private message regarding adding a notify group because you have "
            "to start the bot privately first\. Click on the the button below,"
            " start the bot, then try running `/add_notify_group` in this "
            "group again",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return ConversationHandler.END
    else:
        # send a group message that the bot sent a private message
        keyboard = [[
            InlineKeyboardButton(
                f"{values.RIGHT_POINTING_EMOJI} GO TO PRIVATE CHAT",
                url=f"{values.BOT_URL}"
            ),
        ]]
        update.message.reply_text(
            f"Hey {user_mention}\!\n\nI have sent you a private message which "
            "you can respond to to add a notify group to this group",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2
        )

    return TYPING_NAME


def process_name(update, context):
    context.user_data["messages_to_delete"].append(update.message)
    name = update.message.text.strip()
    chat_id = context.user_data.get("chat_id")
    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
    ]]
    # TODO: I'm not sure if I actually want to change this but I'm like 99%
    # sure this endpoint can't be hit because you can't send empty messages in
    # telegram. 
    if not name:
        # If the notify group name is empty, then send an error message.
        context.user_data["messages_to_delete"].append(
            update.message.reply_text(
                "You did not provide a valid notify group name\. Please enter "
                "a valid notify group name",
                parse_mode=ParseMode.MARKDOWN_V2,
                quote=True, reply_markup=InlineKeyboardMarkup(keyboard)
            )
        )
        return TYPING_NAME

    # Send an error message if the name contains a space
    if ' ' in name:
        alt_name = "\_".join(name.split(" "))
        context.user_data["messages_to_delete"].append(
            update.message.reply_text(
                "You can not have a space in your notify group name\. Here's "
                "an alternative notify group name that you can try instead: "
                f"`{alt_name}`\n\nPlease enter a valid notify group name",
                parse_mode=ParseMode.MARKDOWN_V2,
                quote=True,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        )
        return TYPING_NAME

    # Check if an existing display name is present in the group/private chat.
    number_of_same_name_notify_groups = DBConnection().count_documents(
        "notifygroups",
        {"chat_id": chat_id, "name": name}
    )

    if number_of_same_name_notify_groups > 0:
        context.user_data["messages_to_delete"].append(
            update.message.reply_text(
                "A notify group with that name already exists in the "
                f"_{context.user_data['group_name']}_ group\. Please enter a "
                "unique notify group name",
                parse_mode=ParseMode.MARKDOWN_V2,
                quote=True
            )
        )
        return TYPING_NAME

    # if we've gotten here, it means the group name is unique.
    context.user_data["notify_group_to_add"]["name"] = name
    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_description"
        )
    ]]
    while len(context.user_data["messages_to_delete"]) > 1:
        old_message = context.user_data["messages_to_delete"].pop()
        old_message.delete()

    context.user_data["messages_to_delete"].append(
        context.bot.send_message(
            context.user_data.get("user_id"),
            f"Great\! The notify group name has been set as `{name}`",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    )

    context.user_data["messages_to_delete"].append(
        context.bot.send_message(
            context.user_data.get("user_id"),
            "Enter the **description** for the notify group you want to add "
            f"to _{context.user_data['group_name']}_ group e\.g\. `This group "
            "plays games every weeknight`",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    )
    return TYPING_DESCRIPTION


def process_description(update, context):
    is_callback = False
    if update.callback_query:
        is_callback = True
        update = update.callback_query
        description = update.data
        update.answer()

    if not is_callback:
        context.user_data["messages_to_delete"].append(update.message)
        description = update.message.text.strip()
        if not description:
            # If the group description is empty, then send an error message.
            description_keyboard = [[
                InlineKeyboardButton(
                    f"{values.CANCELLED_EMOJI} CANCEL",
                    callback_data=f"cancel"
                ),
                InlineKeyboardButton(
                    f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
                    callback_data=f"skip_description"
                )
            ]]
            context.user_data["messages_to_delete"].append(
                update.message.reply_text(
                    "You did not provide a valid description\. Please enter a "
                    "valid description",
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=InlineKeyboardMarkup(description_keyboard),
                    quote=True,
                )
            )
            return TYPING_DESCRIPTION

    if is_callback and description == "skip_description":
        status_msg_prefix = "Skipped entry of description\n\n"
        context.user_data["notify_group_to_add"]["description"] = None
    else:
        context.user_data["notify_group_to_add"]["description"] = description
        status_msg_prefix = ("Great\! The group description has been set as "
                             f"`{description}`")

    while len(context.user_data["messages_to_delete"]) > 2:
        old_message = context.user_data["messages_to_delete"].pop()
        old_message.delete()

    context.bot.send_message(
        context.user_data.get("user_id"),
        status_msg_prefix,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    context.user_data["notify_group_to_add"]["invited"] = []
    context.user_data["notify_group_to_add"]["members"] = [
        context.user_data['user_id']
    ]
    DBConnection().insert_one("notifygroups",
                              context.user_data["notify_group_to_add"])

    creator_mention = get_one_mention(
        context.bot, context.user_data['user_id'], context.user_data['chat_id']
    )
    send_loud_and_silent_message(
        context.bot,
        "Processing\.\.\.",
        f"`{context.user_data['notify_group_to_add']['name']}` has been added "
        f"as a notify group by {creator_mention}",
        context.user_data.get("chat_id"),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    stringified_notify_group = stringify_notify_group(
        context.bot, context.user_data["notify_group_to_add"]
    )
    send_loud_and_silent_message(
        context.bot,
        "Processing\.\.\.",
        (f"*You've successfully added a new notify group\.* Below are the "
         "details of the new notify group:\n\n" + stringified_notify_group),
        context.user_data["user_id"],
        parse_mode=ParseMode.MARKDOWN_V2
    )

    context.user_data.clear()
    return ConversationHandler.END


def cancel(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    while context.user_data["messages_to_delete"]:
        old_message = context.user_data["messages_to_delete"].pop()
        old_message.delete()

    context.bot.send_message(
        context.user_data["user_id"],
        f"{values.CANCELLED_EMOJI} Cancelled the process of adding a notify "
        "group"
    )
    context.user_data.clear()
    return ConversationHandler.END

