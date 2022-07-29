from ast import Pass
from tokenize import group
from general import values
from general.db import DBConnection, SELECT_WHERE, INSERT, UPDATE_WHERE
from general.utils import create_sql_array, get_stringized_sql_value
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler


WAITING_FOR_REPLY = 0

def invite(update, context):
    """
    Sends an invite to members that are tagged.
    """
    # Get chat information
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    username = (update.message.from_user['username']
                if update.message.from_user['username'] else 
                update.message.from_user['first_name'])
    mention = f"[{username}](tg://user?id={user_id})"

    # Cancel command if not ran in a group
    if chat_id == user_id:
        update.message.reply_text(
            "You can only run this command in a group",
            quote=True
        )
        return ConversationHandler.END

    # Cancel command if notify group name not provided. 
    if not context.args:
        update.message.reply_text(
            "You need to provide a notify group name to send invites out for",
            quote=True
        )
        return ConversationHandler.END

    # Get the name of the notify group from the arguments
    if len(update.message.entities) > 1:
        start = update.message.entities[0].length
        end = update.message.entities[1].offset-1 
        ng_name = update.message.text[start:end].strip()
    else:
        start = update.message.entities[0].length
        ng_name = update.message.text[start:].strip()

    # Get corresponding notify group from db
    notify_group = DBConnection().fetchone(
        SELECT_WHERE.format(
            "*",
            "NotifyGroups",
            f"telegramChatID = {chat_id} AND name = '{ng_name}'"
        )
    )
    print(chat_id)
    print(ng_name)
    if not notify_group:
        update.message.reply_text(
            "A notify group with that name does not exist.",
            quote=True
        )
        return ConversationHandler.END

    # Cancel command if notify group is closed and no invited users are given
    if len(update.message.entities) <= 1 and notify_group[5]:
        update.message.reply_text(
            f"**Error\!** The notify group `{ng_name}` is a closed group so "
            "you need to tag the users you want to invite to the group as "
            f"follows:\n\n`/invite_to_notify_group {ng_name} "
            "@example_username`",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return ConversationHandler.END

    # Get the list of the invited users
    mentioned_users = []
    for entity in update.message.entities:
        if entity.type == "text_mention":
            # Append their user ids.
            mentioned_users.append(str(entity.user.id))
        elif entity.type == "mention":
            # Append their usernames
            mentioned_users.append(
                update.message.text[entity.offset+1:entity.offset+entity.length]
            )
    print(mentioned_users)

    # Merge the the invited users with the already invited users if they exist 
    if not notify_group[7]:  # no preexisting invited users
        total_invited = set(mentioned_users)
    else:
        total_invited = set(notify_group[7] + mentioned_users)

    # Store notify group in local memory
    context.user_data["notify_group"] = {
        "id": notify_group[0],
        "telegramChatID": notify_group[1],
        "creatorID": notify_group[2],
        "name": notify_group[3],
        "description": notify_group[4],
        "inviteOnly": notify_group[5],
        "members": notify_group[6],
        "invited": total_invited
    }

    # Update invited list of the notify group with the new invited users
    DBConnection().execute(UPDATE_WHERE.format(
        "NotifyGroups",
        f"invited = {create_sql_array(list(total_invited))}",
        f"id = {notify_group[0]}"
    ))

    # Create a formatted list of current members of the notify group
    members_list = "" if notify_group[6] else "None"
    for member_id in notify_group[6]: # The user ids of the members
        member = context.bot.get_chat_member(chat_id, member_id).user
        # TODO: Check for error here, they could have left the chat group. 
        if member.username:
            members_list += (
                f"\- @[{member.username}](tg://user?id={member_id})\n"
            )
        else:
            members_list += (
                f"\- [{member.first_name}](tg://user?id={member_id})\n"
            )

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CROSS_EMOJI} DECLINE",
                callback_data=f"decline_{notify_group[0]}"
            ),
            InlineKeyboardButton(
                f"{values.CHECKMARK_EMOJI} ACCEPT",
                callback_data=f"accept_{notify_group[0]}"
            )
        ]
    ]
    context.user_data["inv_message"] = update.message.reply_text(
        f"You have been invited to the `{ng_name}` notify group\. Below are "
        "the details of this group\. You can choose to either accept this "
        "invite so you will be notified everytime someone does `/notify "
        f"{ng_name}` or you can choose to decline\n\n"
         "__Group Creator__\n"
        f"{mention}\n\n"
        "__Group Name__\n"
        f"`{notify_group[3]}`\n\n"
        "__Group Description__\n"
        f"`{notify_group[4]}`\n\n"
        "__Group Joining Policy__\n" +
        ("Invite Only\n\n" if notify_group[5] else "Open\n\n") +
        "__Current Members__\n" + members_list,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard),
        quote=True
    )
    return WAITING_FOR_REPLY

def reply_to_invite(update, context):
    """
    Grabs the reply, the notify group id, and then 
    """
    update = update.callback_query
    reply, notify_group_id = update.data.split("_")
    update.answer()
    curr_user_id = update.from_user.id
    curr_username = update.from_user.username

    # Grab the notify group from the db 
    notify_group = DBConnection().fetchone(
        SELECT_WHERE.format(
            "*",
            "NotifyGroups",
            f"id = {notify_group_id}"
        )
    )
    # Silently cancel command if the notify group doesn't exist anymore
    if not notify_group:
        return ConversationHandler.END

    # Cancel command if there are no invited users and notify group is
    # invite-only
    if not notify_group[7] and notify_group[5]:
        return ConversationHandler.END

    # Check the invited list to make sure the current user is in it
    user_was_invited = False
    if str(curr_user_id) in notify_group[7]:
        user_was_invited = True
        notify_group[7].remove(str(curr_user_id))
    elif curr_username and curr_username in notify_group[7]:
        user_was_invited = True
        notify_group[7].remove(curr_username)

    # Cancel command if user was not invited and notify group is invite-only
    if not user_was_invited and notify_group[5]:
        return WAITING_FOR_REPLY

    # At this point, anybody who wasn't invited to the closed group has been
    # booted.

    # If the user reply is accept and user doesn't exist in the members list,
    # add the user id to the members list
    if reply == "accept" and not curr_user_id in notify_group[6]:
        # Update members list with the current user id
        DBConnection().execute(UPDATE_WHERE.format(
            "NotifyGroups",
            f"members = {create_sql_array(notify_group[6] + [curr_user_id])}",
            f"id = {notify_group_id}"
        ))

    # End the conversation if there are no more invited users
    if not notify_group[7]:
        return ConversationHandler.END
    
    # Keep listening for other users if there are still more invited
    return WAITING_FOR_REPLY
