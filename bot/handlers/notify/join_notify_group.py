from telegram import ParseMode
from general.db import SELECT_WHERE, UPDATE_WHERE, DBConnection
from general.utils import create_sql_array


def join(update, context):
    """
    This command will join a user as a member for the notify group specified.
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
    
    # Send error message if the user is already a member of the notify group
    if user_id in notify_group[6]:
        update.message.reply_text(
            f"You are already a member of the `{ng_name}` notify group!",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return

    identifier = (update.message.from_user["username"]
                  if "username" in update.message.from_user else str(user_id))
    if notify_group[5] and not identifier in notify_group[7]:
        creator = context.bot.get_chat_member(chat_id, notify_group[2]).user
        creator_label = (f"@{creator['username']}" if creator.username
                    else f"{creator['first_name']}")
        update.message.reply_text(
            f"This notify group is invite-only\. Contact the creator of this "
            f"notify group {creator_label} to get an invite to the `{ng_name}`"
            " notify group",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return
    
    # Add the current user to the notify group's members
    notify_group[6] += [user_id]
    DBConnection().execute(UPDATE_WHERE.format(
        "NotifyGroups",
        f"members = {create_sql_array(notify_group[6])}",
        f"id = {notify_group[0]}"
    ))

    # Remove the user from the invited list if they are in there.  
    if identifier in notify_group[7]:
        notify_group[7].remove(identifier)


    # Notify user they have been added to the notify group, along with the
    # group details
    creator = context.bot.get_chat_member(chat_id, notify_group[2]).user
    creator_label = (f"@{creator['username']}" if creator.username
                        else f"{creator['first_name']}")
    creator_mention = f"[{creator_label}](tg://user?id={user_id})"
    update.message.reply_text(
        f"You have joined the `{ng_name}` notify group\. Below are the "
        "updated details of this group\.\n\n"
         "__Group Creator__\n"
        f"{creator_mention}\n"
        "__Group Name__\n"
        f"`{notify_group[3]}`\n"
        "__Group Description__\n"
        f"`{notify_group[4]}`\n"
        "__Group Joining Policy__\n" +
        ("`Invite Only`\n\n" if notify_group[5] else "`Open`\n\n") +
        "__Current Members__\n" + notify_group[6],
        parse_mode=ParseMode.MARKDOWN_V2,
        quote=True
    )