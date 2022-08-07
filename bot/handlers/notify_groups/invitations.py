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
        notify_group_name = update.message.text[start:end].strip()
    else:
        start = update.message.entities[0].length
        notify_group_name = update.message.text[start:].strip()

    # Get corresponding notify group from db
    notify_group = DBConnection().find_one(
        "notifygroups",
        {"chat_id": chat_id, "name": notify_group_name}
    )

    if not notify_group:
        update.message.reply_text(
            "A notify group with that name does not exist.",
            quote=True
        )
        return ConversationHandler.END

    # Cancel command if notify group is closed and no invited users are given
    if len(update.message.entities) <= 1 and notify_group["invite_only"]:
        update.message.reply_text(
            f"**Error\!** The notify group `{notify_group_name}` is a closed "
            "group so you need to tag the users you want to invite to the "
            "group as follows:\n\n`/invite_to_notify_group "
            f"{notify_group_name} @example_username1 @example_username2 ...`",
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

    # Merge the the invited users with the already invited users if they exist 
    notify_group["invited"] = list(set(notify_group["invited"]).union(set(mentioned_users)))

    # Update invited list of the notify group with the new invited users
    DBConnection().update_one(
        "notifygroups",
        {"_id": notify_group["_id"]},
        {
            "$set": {
                "invited": notify_group["invited"]
            }
        }
    )

    # Create a formatted string of current members of the notify group
    formatted_notify_group_members = "" if notify_group["members"] else "None"
    for member_id in notify_group["members"]: # The user ids of the members
        member = context.bot.get_chat_member(chat_id, member_id).user
        # TODO: Check for error here, they could have left the chat group. 
        if member.username:
            formatted_notify_group_members += (
                f"\- [@{member.username}](tg://user?id={member_id})\n"
            )
        else:
            formatted_notify_group_members += (
                f"\- [{member.first_name}](tg://user?id={member_id})\n"
            )

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CROSS_EMOJI} DECLINE",
                callback_data=f"decline_{notify_group['_id']}"
            ),
            InlineKeyboardButton(
                f"{values.CHECKMARK_EMOJI} ACCEPT",
                callback_data=f"accept_{notify_group['_id']}"
            )
        ]
    ]
    context.user_data["inv_message"] = context.bot.send_message(
        chat_id,
        f"You have been invited to the `{notify_group_name}` notify group\. "
        "Below are the details of this group\. You can choose to either "
        "accept this invite so you will be notified everytime someone does "
        f"`/notify {notify_group_name}` or you can choose to decline\n\n"
         "__Group Creator__\n"
        f"{mention}\n\n"
        "__Group Name__\n"
        f"`{notify_group['name']}`\n\n"
        "__Group Description__\n"
        f"`{notify_group['description']}`\n\n"
        "__Group Joining Policy__\n" +
        ("Invite Only\n\n" if notify_group["invite_only"] else "Open\n\n") +
        "__Current Members__\n" + formatted_notify_group_members,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return WAITING_FOR_REPLY

def reply_to_invite(update, context):
    """
    Grabs the reply, the notify group id, and then 
    """
    update = update.callback_query
    update.answer()
    reply, notify_group_id = update.data.split("_")
    curr_user_id = update.from_user.id
    curr_username = update.from_user.username

    # Grab the notify group from the db 

    notify_group = DBConnection().find_one(
        "notifygroups",
        {"_id": {notify_group_id}}
    )
    # Silently cancel command if the notify group doesn't exist anymore
    if not notify_group:
        return ConversationHandler.END

    # Cancel command if there are no invited users and notify group is
    # invite-only
    if not notify_group["invited"] and notify_group["invite_only"]:
        return ConversationHandler.END

    # Check the invited list to make sure the current user is in it
    if str(curr_user_id) in notify_group["invited"]:
        notify_group["invited"].remove(str(curr_user_id))
    elif curr_username and curr_username in notify_group["invited"]:
        notify_group["invited"].remove(curr_username)
    elif notify_group["invite_only"]:
        return WAITING_FOR_REPLY

    # At this point, anybody who wasn't invited to the closed group has been
    # booted.

    # If the user reply is accept and user doesn't exist in the members list,
    # add the user id to the members list
    if reply == "accept" and not curr_user_id in notify_group["members"]:
        # Update members list with the current user id
        DBConnection().update_one(
            "notifygroups",
            {"_id": notify_group_id},
            {
                "$set": {
                    "members": notify_group["members"] + [curr_user_id]
                }
            }
        )

    # End the conversation if there are no more invited users
    if not notify_group["invited"]:
        return ConversationHandler.END
    
    # Keep listening for other users if there are still more invited
    return WAITING_FOR_REPLY


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
    
    # Send error message if the user is already a member of the notify group
    if user_id in notify_group["members"]:
        update.message.reply_text(
            f"You are already a member of the `{notify_group_name}` notify group\!",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return

    # Set up user information for the creator
    creator = context.bot.get_chat_member(chat_id, notify_group["creator_id"]).user
    creator_tag = (f"@{creator['username']}" if creator.username
                        else f"{creator['first_name']}")
    creator_mention = f"[{creator_tag}](tg://user?id={user_id})"

    user_invite_id = (update.message.from_user["username"]
                      if "username" in update.message.from_user
                      else str(user_id))
    if notify_group["invite_only"] and not user_invite_id in notify_group["invited"]:
        update.message.reply_text(
            f"This notify group is invite-only\. Contact the creator of this "
            f"notify group {creator_mention} to get an invite to the "
            f"`{notify_group_name}` notify group",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return
    
    # Add the current user to the notify group's members
    notify_group["members"] += [user_id]
    DBConnection().update_one(
        "notifygroups",
        {"_id": notify_group["_id"]},
        {
            "_set": {
                "members": notify_group["members"]
            }
        }
    )

    # Remove the user from the invited list if they are in there.  
    if user_invite_id in notify_group["invited"]:
        notify_group["invited"].remove(user_invite_id)


    # Notify user they have been added to the notify group, along with the
    # group details
    update.message.reply_text(
        f"You have joined the `{notify_group_name}` notify group\. Below are the "
        "updated details of this group\.\n\n"
         "__Group Creator__\n"
        f"{creator_mention}\n"
        "__Group Name__\n"
        f"`{notify_group[3]}`\n"
        "__Group Description__\n"
        f"`{notify_group[4]}`\n"
        "__Group Joining Policy__\n" +
        ("`Invite Only`\n\n" if notify_group["invite_only"] else "`Open`\n\n") +
        "__Current Members__\n" + notify_group["members"],
        parse_mode=ParseMode.MARKDOWN_V2,
        quote=True
    )
