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

    ng_name = update.message.text[update.message.entities[0].length:].strip()
    # Send an error message if no notify group name was provided.
    if not ng_name:
        update.message.reply_text(
            "You need to provide a notify group name to join",
            quote=True
        )
        return


    # Get corresponding notify group from db
    notify_group = DBConnection().fetchone(
        SELECT_WHERE.format(
            "*",
            "NotifyGroups",
            f"telegramChatID = {chat_id} AND name = '{ng_name}'"
        )
    )
    # Send error message if notify group doesn't exist.
    if not notify_group:
        update.message.reply_text(
            f"A notify group with the name `{ng_name}` does not exist",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return

    # Send error message if the user is not a part of the notify group
    if not user_id in notify_group[6]:
        update.message.reply_text(
            "You need to be a member of this notify group in order to notify "
            f"the members of it. Try /join_notify_groups `{ng_name}` first.",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return

    # Create a formatted message with all the user mentions.
    mentions = ""
    for member_id in notify_group[6]:
        member = context.bot.get_chat_member(chat_id, member_id).user
        member_label = (f"@{member['username']}" if member.username
                    else f"{member['first_name']}")
        mentions += f"[{member_label}](tg://user?id={member['id']}) "
        

    update.message.reply_text(
        mentions,
        parse_mode=ParseMode.MARKDOWN_V2
    )