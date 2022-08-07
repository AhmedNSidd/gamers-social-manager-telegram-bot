from telegram import ParseMode
from general.utils import create_sql_array
from general.db import INSERT, DBConnection, SELECT_WHERE, UPDATE_WHERE

def notify(update, context):
    """
    This method grabs the name of the notify group provided by the user and
    notifies everyone in that notify group.
    """
    # We need to ensure this command is being run in a group
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    # Send an error if the command is called not in a group chat.
    if chat_id == user_id:
        update.message.reply_text(
            "You can only run this command in a group",
            quote=True
        )
        return

    notify_group_name = update.message.text[update.message.entities[0].length:].strip()
    # Send an error message if no notify group name was provided.
    if not notify_group_name:
        update.message.reply_text(
            "You need to provide a notify group name to join",
            quote=True
        )
        return


    # Get corresponding notify group from db
    notify_group = DBConnection().find_one(
        "notifygroups",
        {"chat_id": chat_id, "name": notify_group_name}
    )
    # Send error message if notify group doesn't exist.
    if not notify_group:
        update.message.reply_text(
            f"A notify group with the name `{notify_group_name}` does not exist",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return

    # Send error message if the user is not a part of the notify group
    if not user_id in notify_group["members"]:
        update.message.reply_text(
            "You need to be a member of this notify group in order to notify "
            f"the members of it. Try /join_notify_groups `{notify_group_name}` first.",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return

    # Create a formatted message with all the user mentions.
    mentions = ""
    for member_id in notify_group["members"]:
        member = context.bot.get_chat_member(chat_id, member_id).user
        member_label = (f"@{member['username']}" if member.username
                    else f"{member['first_name']}")
        mentions += f"[{member_label}](tg://user?id={member['id']}) "

    update.message.reply_text(
        mentions,
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
    
    # Get all the notify groups connected to this group chat.
    notify_groups = list(DBConnection().find(
        "notifygroups",
        {"chat_id": chat_id}
    ))
    # Send an error message if no notify groups exist.
    if not notify_groups:
        update.message.reply_text(
            "No notify groups exist in this group chat",
            quote=True
        )
        return
    
    # Create a nicely formatted message with all the notify groups and send it
    # as a message.
    msg = (
        "Listed below are all the notify groups for this group chat:\n\n"
    )
    for notify_group in notify_groups:
        creator = context.bot.get_chat_member(chat_id, notify_group["creator_id"]).user
        creator_label = (f"@{creator['username']}" if creator.username
                         else f"{creator['first_name']}")
        msg += (f"__Group Name__\n`{notify_group['name']}`\n"
                "__Group Creator__\n"
                f"[{creator_label}](tg://user?id={creator['id']})\n"
                f"__Group Description__\n`{notify_group['description']}`\n"
                f"__Group Joining Policy__\n" +
                ("`Invite Only`\n" if notify_group['invite_only'] else "`Open`\n") +
                "__Current Members__\n")

        if notify_group["members"]:
            for member_id in notify_group["members"]:
                member = context.bot.get_chat_member(chat_id, member_id).user
                member_label = (f"@{member['username']}" if member.username
                         else f"{member['first_name']}")
                msg += f"[{member_label}](tg://user?id={member['id']})\n"
        else:
            msg += "None\n"

    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2,
                              quote=True)
        
