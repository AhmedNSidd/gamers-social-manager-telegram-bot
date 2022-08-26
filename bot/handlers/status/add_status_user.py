import asyncio

from aiohttp import ClientResponseError
from handlers.common import get_one_mention, send_loud_and_silent_message
from external_handlers.apis_wrapper import ApisWrapper
from general import values
from general.db import DBConnection
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
    context.user_data["user_id"] = update.message.from_user.id
    context.user_data["chat_id"] = update.message.chat.id
    context.user_data["group_name"] = (
        update.message.chat.title
        if context.user_data["chat_id"] != context.user_data["user_id"]
        else None
    )
    user_mention = get_one_mention(context.bot, context.user_data["user_id"],
                                   context.user_data["chat_id"])
    context.user_data["messages_to_delete"] = []
    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
    ]]
    try:
        context.user_data["messages_to_delete"].append(
            send_loud_and_silent_message(
                context.bot,
                "Processing\.\.\.", 
                f"Hey {user_mention}\!\n\nWe will add a status user to " + (
                    f"the _{context.user_data['group_name']}_ group "
                    if context.user_data.get("group_name") else
                    "this private chat") +
                "I will ask you for your display name/Xbox Live/PSN/Steam "
                "IDs\. You can choose to add these to your status user, or "
                "choose to skip if would prefer to not connect these services "
                "to your status user\.\n\nYou can also choose to cancel the "
                "process of adding this status user at any point during this "
                "process",
                context.user_data["user_id"],
                parse_mode=ParseMode.MARKDOWN_V2
            )
        )
        context.user_data["messages_to_delete"].append(
            send_loud_and_silent_message(
                context.bot,
                "Processing\.\.\.",
                "Enter the *display name* for the status user you want to add "
                "to " + (
                    f"the _{context.user_data['group_name']}_ group"
                    if context.user_data.get("group_name") else
                    "this private chat") +
                "\n\nYou can not skip this entry",
                context.user_data["user_id"],
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        )
    except Unauthorized:
        if context.user_data.get("group_name"):
            # If process was started in a group, send a group message that the
            # bot was unable to send a private message
            keyboard = [[
                InlineKeyboardButton(
                    f"{values.RIGHT_POINTING_EMOJI} GO TO BOT CHAT TO START "
                                                                        "BOT",
                    url=f"{values.BOT_URL}"
                ),
            ]]
            update.message.reply_text(
                f"Hey {user_mention}\!\n\nThe bot was unable to send you a "
                "private message regarding adding a status user because you "
                "have to start the bot privately first\. Click on the button "
                "below, start the bot, then try running `/add_status_user` in "
                "this group again",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return ConversationHandler.END
    else:
        if context.user_data.get("group_name"):
            # If process was started in a group, send a group message that the bot
            # sent a private message
            keyboard = [[
                InlineKeyboardButton(
                    f"{values.RIGHT_POINTING_EMOJI} GO TO PRIVATE CHAT",
                    url=f"{values.BOT_URL}"
                ),
            ]]
            update.message.reply_text(
                f"Hey {user_mention}\!\n\nI have sent you a private message "
                "which you can respond to to add your status user to this "
                "group",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )

    return TYPING_DISPLAY_NAME


def process_display_name(update, context):
    display_name = update.message.text.strip()
    chat_id = context.user_data.get("chat_id")
    context.user_data["messages_to_delete"].append(update.message)
    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
    ]]
    if not display_name:
        # If the display name is empty, then send an error message.
        context.user_data["messages_to_delete"].append(update.message.reply_text(
            "You did not provide a valid display name\. Please enter a unique "
            "display name", parse_mode=ParseMode.MARKDOWN_V2, quote=True
        ))
        return TYPING_DISPLAY_NAME

    # Check if an existing display name is present in the group/private chat.
    users_with_the_same_name = DBConnection().count_documents(
        "statususers",
        {"chat_id": chat_id, "display_name": display_name}
    )
    if users_with_the_same_name > 0:
        context.user_data["messages_to_delete"].append(update.message.reply_text(
            f"Somebody with that display name already exists in " +
            (f"the _{context.user_data['group_name']}_ group"
             if context.user_data.get("group_name") else
             "this private chat") +
            "'s status\. Please enter a unique display name",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        ))
        return TYPING_DISPLAY_NAME

    # if we've gotten here, it means the display name is unique.
    context.user_data["display_name"] = display_name
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
    while len(context.user_data["messages_to_delete"]) > 1:
        old_message = context.user_data["messages_to_delete"].pop()
        old_message.delete()

    context.bot.send_message(
        context.user_data.get("user_id"),
        f"Great\! Your display name has been set as *{display_name}*\n\n",
        parse_mode=ParseMode.MARKDOWN_V2
    )

    context.user_data["messages_to_delete"].append(context.bot.send_message(
        context.user_data.get("user_id"),
        "Now enter your *Xbox Gamertag*",
        reply_markup=InlineKeyboardMarkup(keyboard),
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
            context.user_data["messages_to_delete"].append(update.message.reply_text(
                "You did not provide a valid Xbox Gamertag\. Please enter a "
                "valid Xbox Gamertag",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return TYPING_XBOX_GAMERTAG

    if is_callback and xbox_gamertag == "skip_xbox_gamertag":
        status_msg_prefix = f"Skipped Xbox Live setup\n\n"
    else:
        context.user_data["messages_to_delete"].append(update.message.reply_text(
            f"{values.RAISED_HAND_EMOJI} Please hold as we process your Xbox "
            "Gamertag\. This might take around 10 seconds",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        ))
        try:
            context.user_data["xbox_account_id"] = asyncio.run(
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

        context.user_data["xbox_gamertag"] = xbox_gamertag
        status_msg_prefix = ("Great\! Your Xbox Gamertag has been set as "
                             f"*{xbox_gamertag}*\n\n")

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
    else:
        context.user_data["messages_to_delete"].append(update.message.reply_text(
            f"{values.RAISED_HAND_EMOJI} Please hold as we process your PSN "
            "Online ID\. This might take around 5 seconds",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        ))
        try:
            context.user_data['psn_account_id'] = asyncio.run(
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

        context.user_data["psn_online_id"] = psn_online_id
        status_msg_prefix = ("Great\! Your PSN Online ID has been set as "
                             f"*{psn_online_id}*\n\n")

    while len(context.user_data["messages_to_delete"]) > 1:
        old_message = context.user_data["messages_to_delete"].pop()
        old_message.delete()

    del context.user_data["messages_to_delete"]

    ret = process_new_status_user(context)
    if type(ret) == int:
        return ret

    if context.user_data.get("group_name"):
        mention = (f"[{username}](tg://user?id="
                   f"{context.user_data.get('user_id')})")
        context.bot.send_message(
            context.user_data.get("chat_id"),
            f"*{context.user_data.get('display_name')}* has been added to the "
            f"/status command by {mention}",
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
        "details of your new status user:\n\n"
        "__Display Name__\n"
        f"`{context.user_data['display_name']}`\n\n"
        "__Xbox Gamertag__\n"
        f"`{context.user_data.get('xbox_gamertag')}`\n\n"
        "__PSN Online ID__"
        f"\n`{context.user_data.get('psn_online_id')}`\n\n"
        "Added by [you]"
        f"(tg://user?id={context.user_data['user_id']}) in " +
        (f"the _{context.user_data['group_name']}_ group"
         if context.user_data.get("group_name") else
         "this private chat"),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    context.user_data.clear()
    return ConversationHandler.END


def process_new_status_user(context):
    if (not context.user_data.get("xbox_gamertag") and
            not context.user_data.get("psn_online_id")):
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
        context.user_data
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
