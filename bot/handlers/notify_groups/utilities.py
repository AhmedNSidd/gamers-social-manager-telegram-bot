import re

from telegram import ParseMode
from telegram.error import BadRequest
from general.db import DBConnection
from handlers.common import get_one_mention, send_loud_and_silent_message,\
                            escape_text
from handlers.notify_groups.common import stringify_notify_group


def notify(update, context):
    """
    This method grabs the name of the notify group provided by the user and
    notifies everyone in that notify group.
    """
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    curr_user_mention = get_one_mention(context.bot, user_id, chat_id)

    # Send an error if the command is called not in a group chat.
    if chat_id == user_id:
        update.message.reply_text(
            "You can only run this command in a group",
            quote=True
        )
        return

    # Send an error message if no notify group name was provided.
    if not context.args:
        update.message.reply_text(
            "You need to provide a notify group name to notify e\.g\. "
            "`/notify group_name`",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return

    # Get the notify group name and optional message (if it exists)
    notify_group_name = context.args[0]
    notify_group_message = (" ".join(context.args[1:])
                            if len(context.args) > 1 else None)

    # Get corresponding notify group from db
    notify_group = DBConnection().find_one(
        "notifygroups",
        {
            "chat_id": chat_id,
            "name": re.compile('^' + notify_group_name + '$', re.IGNORECASE)
        }
    )

    # Send error message if notify group doesn't exist.
    if not notify_group:
        update.message.reply_text(
            f"A notify group with the name `{notify_group_name}` does not "
            "exist",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return

    # Send error message if the user is not a part of the members of the
    # notify group, with instructions on how that can be fixed.
    if (not user_id in notify_group["members"]
        and notify_group["creator_id"] != user_id):
        notify_group_creator_mention = get_one_mention(
            context.bot, notify_group['creator_id'], chat_id
        )
        send_loud_and_silent_message(
            context.bot,
            "Processing\.\.\.",
            "You need to be a member of this notify group in order to notify "
            "the members of it\. You can ask the creator of this notify group,"
            f" {notify_group_creator_mention}\. The creator can invite you "
            "using the following command:\n\n/invite\_to\_notify\_group "
            f"{escape_text(notify_group['name'])} {curr_user_mention}",
            chat_id,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    # Create the notify message, tagging all the notify group members
    notify_msg = ""
    for member_id in notify_group["members"]:
        if user_id == member_id:
            continue
        user_mention = get_one_mention(context.bot, member_id, chat_id)
        notify_msg += f"{user_mention} "

    if notify_group_message:
        notify_msg += (f"\n\n{curr_user_mention} is saying "
                       f"`{notify_group_message}`")
    else:
        notify_msg += f"\n\n{curr_user_mention} wants your attention"

    # Delete the user's "/notify" message
    try:
        update.message.delete()
    except BadRequest:
        # This means that our bot doesn't have the appropriate permissions to
        # delete a message in the group chat so we can just silently fail
        pass

    # Send the notify message, tagging all the notify group members
    update.message.reply_text(
        notify_msg,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def list_notify_groups(update, context):
    """
    This method lists all the notify groups connected to the group chat that
    the command is called in. If it's called in a private group chat, then
    respond with an error.
    """
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    # Send an error if the command is called not in a group chat.
    if chat_id == user_id:
        update.message.reply_text(
            "You can only run this command in a group",
            quote=True
        )
        return

    if context.args:
        # Use the notify group names that are given as command arguments if
        # there are context.args
        regex_string = "^"
        for arg in context.args:
            regex_string += f"{arg}|"
        regex_string = regex_string[:-1] + "$"
        compiled_regex = re.compile(regex_string, re.IGNORECASE)
        notify_groups = sorted(
            DBConnection().find(
                "notifygroups",
                {
                    "chat_id": chat_id,
                    "name": compiled_regex
                }
            ),
            key=lambda notify_group: notify_group["name"]
        )
    else:
        # Get all the notify groups connected to this group chat if there are
        # no context arguments
        notify_groups = sorted(DBConnection().find(
            "notifygroups",
            {"chat_id": chat_id}
        ), key=lambda notify_group: notify_group["name"])

    # Send an error message if no notify groups exist.
    if not notify_groups:
        update.message.reply_text(
            "No notify groups exist in this group chat",
            quote=True
        )
        return

    # Create a nicely formatted message with all the notify groups and send it
    # as a message.
    if context.args:
        # If there were notify groups specified, then ensure the user knows
        # that not all the notify groups were returned for this group chat.
        msg = (
            "Listed below are the valid notify groups you requested for this "
            "group chat \(sorted alphabetically\):\n\n"
        )
    else:
        # If no notify groups were specified, let the user know we are
        # returning them all the notify groups found connected to this group
        # chat
        msg = (
            "Listed below are all the notify groups for this group chat "
            "\(sorted alphabetically\):\n\n"
        )
    # msg += "`\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-`\n"
    for notify_group in notify_groups:
        msg += f"{stringify_notify_group(context.bot, notify_group)}\n\n"
        # msg += "`\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-`\n"

    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2,
                              quote=True)
