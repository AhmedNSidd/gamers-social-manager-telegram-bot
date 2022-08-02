from telegram import ParseMode
from general.db import DBConnection, SELECT_WHERE


def list(update, context):
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
    notify_groups = DBConnection().fetchall(
        SELECT_WHERE.format(
            "*",
            "NotifyGroups",
            f"telegramChatID = {chat_id}"
        )
    )
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
        creator = context.bot.get_chat_member(chat_id, notify_group[2]).user
        creator_label = (f"@{creator['username']}" if creator.username
                         else f"{creator['first_name']}")
        msg += (f"__Group Name__\n`{notify_group[3]}`\n"
                "__Group Creator__\n"
                f"[{creator_label}](tg://user?id={creator['id']})\n"
                f"__Group Description__\n`{notify_group[4]}`\n"
                f"__Group Joining Policy__\n" +
                ("`Invite Only`\n" if notify_group[5] else "`Open`\n") +
                "__Current Members__\n")

        if notify_group[6]:
            for member_id in notify_group[6]:
                member = context.bot.get_chat_member(chat_id, member_id).user
                member_label = (f"@{member['username']}" if member.username
                         else f"{member['first_name']}")
                msg += f"[{member_label}](tg://user?id={member['id']})\n"
        else:
            msg += "None\n"

    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2,
                              quote=True)
        
