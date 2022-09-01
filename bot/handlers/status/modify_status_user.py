
import asyncio

from aiohttp import ClientResponseError
from bson.objectid import ObjectId
from handlers.common import get_one_mention
from general import values
from general.db import DBConnection
from external_handlers.apis_wrapper import ApisWrapper
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler
from telegram.error import Unauthorized


# Conversation stats for the CommandHandler for modify_status_user
MAIN_MENU, EDITING_DISPLAY_NAME, EDITING_XBOX_GAMERTAG, \
    EDITING_PSN_ONLINE_ID, DELETING_EMPTY_STATUS_USER, \
    DELETING_STATUS_USER = range(6)


def start(update, context):
    """
    This handler will serve as the start of a conversation with the user on
    which StatusUsers they would like to modify. The user has access to all of
    their StatusUsers including any StatusUsers that exist of a group that they
    are an admin of. Which StatusUsers are presented to the user is dependent
    on where the user actually enters the command.
    """
    is_callback = False
    if update.callback_query:
        # It could be only be a callback if the interface already exists and
        # the user decided to go back to this page
        is_callback = True
        update = update.callback_query
        update.answer()

    # If we get here due to a callback, then we need to use the preexisting
    # user id, group names, etc. But if a fresh commmand is executed then we
    # need to get fresh IDs.
    if not is_callback:
        context.user_data["user_id"] = update.message.from_user.id
        context.user_data["chat_id"] = update.message.chat.id
        context.user_data["user_mention"] = get_one_mention(
            context.bot,
            context.user_data["user_id"],
            context.user_data["chat_id"]
        )
        context.user_data["group_name"] = (
            update.message.chat.title
            if context.user_data["chat_id"] != context.user_data["user_id"]
            else None
        )

    user_group_privilege = context.bot.get_chat_member(
        context.user_data["chat_id"], context.user_data["user_id"]
    ).status

    if (user_group_privilege == "creator"
            or user_group_privilege == "administrator"):
        current_users_status_users = DBConnection().find(
            "statususers", {"chat_id": context.user_data["chat_id"]}
        )
    else:
        current_users_status_users = DBConnection().find(
            "statususers", {"chat_id": context.user_data["chat_id"],
                            "user_id": context.user_data["user_id"]}
        )

    if not current_users_status_users:
        if context.user_data["group_name"]:
            error_msg = (
                "You have no status users to modify in the "
                f"{context.user_data['group_name']} group\. Please add one "
                "first by entering `/add_status_user` in that group chat"
            )
        else:
            error_msg = (
                "You have no status users to modify in this private chat\. "
                "Please add one first by entering `/add_status_user` in this "
                "chat"
            )

        if is_callback:
            update.message.edit_text(error_msg,
                                     parse_mode=ParseMode.MARKDOWN_V2)
        else:
            update.message.reply_text(error_msg,
                                      parse_mode=ParseMode.MARKDOWN_V2)
        return ConversationHandler.END

    if context.user_data.get("group_name"):
        my_status_users = {}
        other_status_users = {}
        for status_user in current_users_status_users:
            if status_user["user_id"] == context.user_data["user_id"]:
                my_status_users[status_user["_id"]
                                ] = status_user["display_name"]
            else:
                other_status_users[status_user["_id"]
                                   ] = status_user["display_name"]

        status_user_msg = (
            "Choose to modify either your or someone else's status user in "
            f"the _{context.user_data.get('group_name')}_ group\."
        )
    else:
        my_status_users = {}
        for status_user in current_users_status_users:
            my_status_users[status_user["_id"]] = status_user["display_name"]

        other_status_users = {}
        status_user_msg = (
            "Choose to modify a status user in this private chat"
        )

    # Create the keyboard with all the Status users of the group
    keyboard = [[]]
    for id in my_status_users:
        if len(keyboard[-1]) < 2:
            keyboard[-1].append(InlineKeyboardButton(
                f"{my_status_users[id]} (Yours)", callback_data=str(id)
            ))
        else:
            keyboard.append([InlineKeyboardButton(
                f"{my_status_users[id]} (Yours)", callback_data=str(id)
            )])

    for id in other_status_users:
        if len(keyboard[-1]) < 2:
            keyboard[-1].append(InlineKeyboardButton(
                f"{other_status_users[id]} (Others)", callback_data=str(id)
            ))
        else:
            keyboard.append([InlineKeyboardButton(
                f"{other_status_users[id]} (Others)", callback_data=str(id)
            )])

    keyboard_markup = InlineKeyboardMarkup(keyboard)
    if is_callback:
        # This is the case where someone presses the "back" button to go back
        # to the home screen of the interface
        update.message.edit_text(
            status_user_msg, reply_markup=keyboard_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return MAIN_MENU
    
    try:
        # This is the case where someone just typed /modify_status_user
        context.bot.send_message(
            context.user_data["user_id"], status_user_msg,
            reply_markup=keyboard_markup, parse_mode=ParseMode.MARKDOWN_V2
        )
    except Unauthorized:
        if context.user_data.get("group_name"):
            keyboard = [[
                InlineKeyboardButton(
                    f"{values.RIGHT_POINTING_EMOJI} GO TO BOT CHAT TO START "
                                                                        "BOT",
                    url=f"{values.BOT_URL}"
                ),
            ]]
            update.message.reply_text(
                f"Hey {context.user_data['user_mention']}\!\n\nThe bot was "
                "unable to send you a private message regarding modifying a "
                "status user because you have to start the bot privately "
                "first\. Click on the button below, start the bot, then try "
                "running `/modify_status_user` in this group again",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2,
                quote=True
            )
    else:
        if context.user_data.get("group_name"):
            keyboard = [[
                InlineKeyboardButton(
                    f"{values.RIGHT_POINTING_EMOJI} GO TO PRIVATE CHAT",
                    url=f"{values.BOT_URL}"
                ),
            ]]
            update.message.reply_text(
                f"Hey {context.user_data['user_mention']}\!\n\nI have sent "
                "you a private message which you can use to modify your "
                "status users connected to this group",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2,
                quote=True
            )

    return MAIN_MENU


def edit_or_delete(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    user_id = context.user_data["user_id"]
    query_for_status_user = {"_id": ObjectId(update.data)}
    status_user_to_modify = DBConnection().find_one("statususers",
                                                    query_for_status_user)

    status_user_msg = (
        "__Display Name__\n"
        f"`{status_user_to_modify['display_name']}`\n\n"
        "__Xbox Gamertag__\n"
        f"`{status_user_to_modify['xbox_gamertag']}`\n\n"
        "__PSN Online ID__"
        f"\n`{status_user_to_modify['psn_online_id']}`\n\n" +
        (f"Added by [this user]"
         f"(tg://user?id={status_user_to_modify['user_id']})"
         if status_user_to_modify["user_id"] != user_id else
         "Added by [you]"
         f"(tg://user?id={status_user_to_modify['user_id']})")
    )
    context.user_data['status_user_to_modify'] = status_user_to_modify
    keyboard = [
        [
            InlineKeyboardButton(f"{values.CROSS_EMOJI} DELETE",
                                 callback_data=f"delete_{update.data}")
        ],
        [
            InlineKeyboardButton(f"{values.LEFT_POINTING_EMOJI} GO BACK",
                                 callback_data="modify_status_user")
        ]
    ]
    if status_user_to_modify["user_id"] == user_id:
        keyboard[0].insert(0, InlineKeyboardButton(
            f"{values.PENCIL_EMOJI} EDIT", callback_data=f"edit_{update.data}"
        ))

    update.edit_message_text(
        status_user_msg, reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    return MAIN_MENU


def edit(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    user_id = context.user_data.get("user_id")
    group_name = context.user_data['group_name']
    status_user_to_edit = context.user_data.get("status_user_to_modify")

    update.message.delete()
    context.user_data["messages"] = []
    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        f"Hey {update.from_user.first_name}\! We will edit the status user "
        f"*{status_user_to_edit['display_name']}*\n\nI will "
        "ask you to edit your display name/Xbox Live/PSN/Steam IDs\. You can "
        "choose to edit these to something else, or choose to skip if you "
        "would prefer not to edit these entries and leave them as it is\.\n\n"
        "You can also choose to cancel any edits made to the status user at "
        "any point during this process\n\nFinally you will also have the "
        "option of disconnecting any of your gaming IDs \(Xbox Live/PSN/Steam"
        "\)from this status user so the status of that service will not be "
        "displayed anymore",
        parse_mode=ParseMode.MARKDOWN_V2
    ))
    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        "Below are the details of the status user you're editing:\n\n"
        "__Display Name__\n"
        f"`{status_user_to_edit['display_name']}`\n\n"
        "__Xbox Gamertag__\n"
        f"`{status_user_to_edit['xbox_gamertag']}`\n\n"
        "__PSN Online ID__\n"
        f"`{status_user_to_edit['psn_online_id']}`\n\n" +
        f"Added by [you](tg://user?id={user_id}) in " +
        (f"the _{group_name}_ group" if group_name else "this private chat"),
        parse_mode=ParseMode.MARKDOWN_V2
    ))
    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} DISCARD EDITS",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_display_name"
        ),
    ]]
    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        "Enter the new *display name* for your status user \(currently set as "
        f"*{status_user_to_edit['display_name']}*\)",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    ))
    return EDITING_DISPLAY_NAME


def process_display_name(update, context):
    # Here we have to ensure that the display name that the user has chosen is:
    # not empty, but also is unique relative to where they are trying to add it
    is_callback = False
    if update.callback_query:
        is_callback = True
        update = update.callback_query
        new_display_name = update.data
        update.answer()

    chat_id = context.user_data.get("chat_id")
    user_id = context.user_data.get("user_id")
    group_name = context.user_data.get("group_name")
    status_user_to_edit = context.user_data.get("status_user_to_modify")

    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} DISCARD EDITS",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_display_name"
        ),
    ]]
    if not is_callback:
        context.user_data["messages"].append(update.message)
        new_display_name = update.message.text.strip()

        if not new_display_name:
            context.user_data["messages"].append(update.message.reply_text(
                "You did not provide a valid display name\. Please enter a "
                "unique display name",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_DISPLAY_NAME
        elif new_display_name == status_user_to_edit["display_name"]:
            context.user_data["messages"].append(update.message.reply_text(
                "The display name you entered is the same as the previously "
                "set display name\. Please enter a new display name or skip "
                "this entry",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_DISPLAY_NAME

        users_with_the_same_name = DBConnection().count_documents(
            "statususers",
            {"chat_id": chat_id, "display_name": new_display_name}
        )
        if users_with_the_same_name > 0:
            context.user_data["messages"].append(update.message.reply_text(
                "Somebody with that display name already exists in the " +
                (f"the _{group_name}_ group" if group_name else
                 "this private chat") +
                "'s status\. Please enter a unique display name",
                reply_markup=InlineKeyboardButton(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2,
                quote=True
            ))
            return EDITING_DISPLAY_NAME

    if is_callback and new_display_name == "skip_display_name":
        display_name_edit_msg = "Skipped editting your display name"
    else:
        display_name_edit_msg = (
            f"Great\! Your display name has been set as *{new_display_name}*"
        )
        status_user_to_edit["display_name"] = new_display_name

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} DISCARD EDITS",
                callback_data=f"cancel"
            ),
            InlineKeyboardButton(
                f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
                callback_data=f"skip_xbox_gamertag"
            ),
        ]
    ]
    if status_user_to_edit["xbox_gamertag"]:
        keyboard.append([
            InlineKeyboardButton(
                f"{values.CONTROLLER_EMOJI} DISCONNECT XBOX LIVE ACCOUNT",
                callback_data=f"disconnect"
            ),
        ])
    while len(context.user_data["messages"]) > 2:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    context.user_data["messages"].append(context.bot.send_message(
        user_id, display_name_edit_msg, parse_mode=ParseMode.MARKDOWN_V2
    ))

    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        "Enter the new *Xbox Gamertag* \(currently " +
        (f"set as *{status_user_to_edit['xbox_gamertag']}*\)"
         if status_user_to_edit['xbox_gamertag'] else
         "not set as anything\)"),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    ))

    return EDITING_XBOX_GAMERTAG


def process_xbox_gamertag(update, context):
    is_callback = False
    if update.callback_query:
        is_callback = True
        update = update.callback_query
        xbox_gamertag = update.data
        update.answer()

    user_id = context.user_data.get("user_id")
    status_user_to_edit = context.user_data.get("status_user_to_modify")

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} DISCARD EDITS",
                callback_data=f"cancel"
            ),
            InlineKeyboardButton(
                f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
                callback_data=f"skip_xbox_gamertag"
            ),
        ]
    ]
    if status_user_to_edit["xbox_gamertag"]:
        keyboard.append([
            InlineKeyboardButton(
                f"{values.CONTROLLER_EMOJI} DISCONNECT XBOX LIVE ACCOUNT",
                callback_data=f"disconnect"
            )
        ])
    if not is_callback:
        context.user_data["messages"].append(update.message)
        xbox_gamertag = update.message.text.strip()

        if not xbox_gamertag:
            context.user_data["messages"].append(update.message.reply_text(
                "You did not provide a valid Xbox Gamertag\. Please enter a "
                "valid Xbox Gamertag",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_XBOX_GAMERTAG
        elif xbox_gamertag == status_user_to_edit["xbox_gamertag"]:
            context.user_data["messages"].append(update.message.reply_text(
                "The Xbox Gamertag you entered is the same as the previously "
                "set Xbox Gamertag\. Please enter a new Xbox Gamertag",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_XBOX_GAMERTAG

    # Now we simply want to insert the Xbox Gamertag and the Xbox ID in the
    # corresponding record in the db.
    if is_callback and xbox_gamertag == "disconnect":
        status_user_to_edit["xbox_gamertag"] = None
        status_user_to_edit["xbox_account_id"] = None
        xbox_modification_msg = ("Great\! You have disconnected your Xbox "
                                 "Gamertag from this status user")
    elif is_callback and xbox_gamertag == "skip_xbox_gamertag":
        xbox_modification_msg = "Skipped editing your Xbox Gamertag"
    else:
        context.user_data["messages"].append(update.message.reply_text(
            f"{values.RAISED_HAND_EMOJI} Please hold as we process your Xbox "
            "Gamertag\. This might take around 10 seconds",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        ))
        try:
            status_user_to_edit["xbox_account_id"] = asyncio.run(
                ApisWrapper().get_account_id_from_gamertag(xbox_gamertag)
            )
        except ClientResponseError as cre:
            if cre.status == 404:
                context.user_data["messages"][-1].edit_text(
                    "The Xbox Gamertag you entered could not be found\! "
                    "Please enter a valid Xbox Gamertag",
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return EDITING_XBOX_GAMERTAG

        status_user_to_edit["xbox_gamertag"] = xbox_gamertag
        xbox_modification_msg = ("Great\! Your Xbox Gamertag has been set as "
                                 f"*{xbox_gamertag}*")

    while len(context.user_data["messages"]) > 3:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} DISCARD EDITS",
                callback_data=f"cancel"
            ),
            InlineKeyboardButton(
                f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
                callback_data=f"skip_psn_online_id"
            ),
        ]
    ]
    if status_user_to_edit["psn_online_id"]:
        keyboard.append([
            InlineKeyboardButton(
                f"{values.CONTROLLER_EMOJI} DISCONNECT PSN ACCOUNT",
                callback_data=f"disconnect"
            )
        ])
    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        xbox_modification_msg,
        parse_mode=ParseMode.MARKDOWN_V2
    ))
    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        "Now enter the new *PSN Online ID* \(currently " +
        (f"set as *{status_user_to_edit['psn_online_id']}*\)"
         if status_user_to_edit['psn_online_id'] else
         "not set as anything\)"),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    ))
    return EDITING_PSN_ONLINE_ID


def process_psn_online_id(update, context):
    is_callback = False
    if update.callback_query:
        is_callback = True
        update = update.callback_query
        psn_online_id = update.data
        update.answer()

    group_name = context.user_data.get("group_name")
    user_id = context.user_data.get("user_id")
    status_user_to_edit = context.user_data.get("status_user_to_modify")

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} DISCARD EDITS",
                callback_data=f"cancel"
            ),
            InlineKeyboardButton(
                f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
                callback_data=f"skip_psn_online_id"
            ),
        ],
    ]
    if status_user_to_edit["psn_online_id"]:
        keyboard.append([
            InlineKeyboardButton(
                f"{values.CONTROLLER_EMOJI} DISCONNECT PSN ACCOUNT",
                callback_data=f"disconnect"
            )
        ])
    if not is_callback:
        context.user_data["messages"].append(update.message)
        psn_online_id = update.message.text.strip()
        if not psn_online_id:
            context.user_data["messages"].append(update.message.reply_text(
                "You did not provide a valid PSN Online ID\. Please enter a "
                "valid PSN Online ID",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_PSN_ONLINE_ID
        elif psn_online_id == status_user_to_edit["psn_online_id"]:
            context.user_data["messages"].append(update.message.reply_text(
                "The PSN Online ID you entered is the same as the previously "
                "set PSN Online ID\. Please enter a new PSN Online ID",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_PSN_ONLINE_ID

    # Now we simply want to update the PSN Online ID in the corresponding
    # record in the db.
    if is_callback and psn_online_id == "disconnect":
        status_user_to_edit['psn_online_id'] = None
        status_user_to_edit['psn_account_id'] = None
        psn_modification_msg = ("Great\! You have disconnected your PSN Online"
                                " ID from this status user")
    elif is_callback and psn_online_id == "skip_psn_online_id":
        psn_modification_msg = "Skipped editing your PSN Online ID"
    else:
        context.user_data["messages"].append(update.message.reply_text(
            f"{values.RAISED_HAND_EMOJI} Please hold as we process your PSN "
            "Online ID\. This might take around 5 seconds",
            parse_mode=ParseMode.MARKDOWN_V2
        ))
        try:
            status_user_to_edit['psn_account_id'] = asyncio.run(
                ApisWrapper().get_account_id_from_online_id(psn_online_id)
            )
        except ClientResponseError as cre:
            if cre.status == 404:
                context.user_data["messages"][-1].edit_text(
                    "The PSN Online ID you entered could not be found\! "
                    "Please enter a valid PSN Online ID",
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return EDITING_PSN_ONLINE_ID

        status_user_to_edit['psn_online_id'] = psn_online_id
        psn_modification_msg = ("Great\! Your PSN Online ID has been set as "
                                f"*{psn_online_id}*")

    while len(context.user_data["messages"]) > 4:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    ret = process_edited_status_user(context)
    if type(ret) == int:
        return ret

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK TO YOUR STATUS USER",
                callback_data=f"{status_user_to_edit['_id']}"
            )
        ]
    ]

    context.bot.send_message(user_id, psn_modification_msg,
                             parse_mode=ParseMode.MARKDOWN_V2)

    context.bot.send_message(
        user_id,
        f"*You've successfully updated your status user\.* Below are the "
        "details of your new status user:\n\n"
        "__Display Name__\n"
        f"`{status_user_to_edit['display_name']}`\n\n"
        "__Xbox Gamertag__\n"
        f"`{status_user_to_edit['xbox_gamertag']}`\n\n"
        "__PSN Online ID__"
        f"\n`{status_user_to_edit['psn_online_id']}`\n\n"
        "Added by [you]"
        f"(tg://user?id={status_user_to_edit['user_id']}) in " +
        (f"the _{group_name}_ group" if group_name else "this private chat"),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    return MAIN_MENU


def process_edited_status_user(context):
    user_id = context.user_data.get("user_id")
    status_user_to_edit = context.user_data.get("status_user_to_modify")
    status_user_to_edit['display_name'] = status_user_to_edit.get(
        "display_name")

    if not status_user_to_edit["xbox_gamertag"] and not status_user_to_edit["psn_online_id"]:
        group_name = context.user_data.get("group_name")
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{values.CANCELLED_EMOJI} CANCEL CHANGES",
                    callback_data="cancel"
                ),
                InlineKeyboardButton(
                    f"{values.CHECKMARK_EMOJI} DELETE {status_user_to_edit['display_name']}",
                    callback_data=f"confirm_delete_{status_user_to_edit['_id']}"
                ),
            ]
        ]
        context.user_data["messages"].append(context.bot.send_message(
            user_id,
            "Warning\! Since you have no Xbox Gamertag or PSN Online ID "
            f"connected to the `{status_user_to_edit['display_name']}` status user\. It "
            f"will be deleted from " +
            f"the _{group_name}_ group" if group_name else "this private chat"
            + "\n\nIf you didn't mean to do this, you can cancel your changes "
            "below, or confirm it, and your status user will be deleted",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(keyboard)
        ))
        return DELETING_EMPTY_STATUS_USER

    DBConnection().update_one(
        "statususers",
        {"_id": ObjectId(status_user_to_edit["_id"])},
        {"$set": {
            "display_name": status_user_to_edit["display_name"],
            "xbox_gamertag": status_user_to_edit["xbox_gamertag"],
            "xbox_account_id": status_user_to_edit["xbox_account_id"],
            "psn_online_id": status_user_to_edit["psn_online_id"],
            "psn_account_id": status_user_to_edit["psn_account_id"]
        }}
    )


def cancel(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    user_id = context.user_data.get("user_id")
    status_user_to_edit = context.user_data.get("status_user_to_modify")
    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK TO YOUR STATUS USER",
                callback_data=f"{status_user_to_edit['_id']}"
            )
        ]
    ]
    while context.user_data["messages"]:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    context.bot.send_message(
        user_id,
        f"{values.CANCELLED_EMOJI} Cancelled the process of editing your "
        "status user",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


def delete(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    group_name = context.user_data.get("group_name")
    status_user_to_delete = context.user_data["status_user_to_modify"]

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK",
                callback_data=f"{status_user_to_delete['_id']}"
            ),
            InlineKeyboardButton(
                f"{values.CHECKMARK_EMOJI} CONFIRM",
                callback_data=f"confirm_delete_{status_user_to_delete['_id']}"
            )
        ]
    ]
    if group_name != None:
        status_user_deletion_msg = (
            "Confirm deletion of the status user "
            f"*{status_user_to_delete['display_name']}* in the _{group_name}_ "
            "group")
    else:
        status_user_deletion_msg = (
            f"Confirm deletion of the status user "
            f"*{status_user_to_delete['display_name']}* in this private chat"
        )

    update.edit_message_text(
        status_user_deletion_msg, reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    return DELETING_STATUS_USER


def confirm_delete(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    group_name = context.user_data.get("group_name")
    status_user_to_delete = context.user_data["status_user_to_modify"]

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK TO STATUS USERS",
                callback_data=f"modify_status_user"
            ),
        ]
    ]

    DBConnection().delete_one("statususers",
                              {"_id": ObjectId(status_user_to_delete['_id'])})

    if group_name != None:
        status_user_deletion_msg = (
            f"Deleted *{status_user_to_delete['display_name']}* from the "
            f"_{group_name}_ group"
        )
    else:
        status_user_deletion_msg = (
            f"Deleted *{status_user_to_delete['display_name']}* from the "
            "private chat"
        )

    if group_name != None:
        user_username = update.from_user['username']
        mention = (
            f"[{user_username}](tg://user?id={context.user_data['user_id']})"
        )
        context.bot.send_message(
            context.user_data["chat_id"],
            f"*{status_user_to_delete['display_name']}* has been removed from "
            f"the /status command by {mention}",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    update.edit_message_text(status_user_deletion_msg,
                             reply_markup=InlineKeyboardMarkup(keyboard),
                             parse_mode=ParseMode.MARKDOWN_V2)

    return MAIN_MENU
