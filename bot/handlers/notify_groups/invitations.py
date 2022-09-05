from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from general.db import DBConnection
from general import values
from handlers.common import get_user, get_one_mention, get_many_mentions, send_loud_and_silent_message
from handlers.notify_groups.common import stringify_notify_group
from bson import ObjectId

WAITING_FOR_REPLY = 0


def invite(update, context):
    """
    Sends an invite to members that are tagged for a notify group
    """
    # Get chat information
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

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

    # Get the name of the notify group from message entities
    notify_group_name = context.args[0]

    # Cancel command if no users were invited to the notify group
    if len(update.message.entities) <= 1:
        update.message.reply_text(
            "**Error\!** You need to tag the users you want to invite to the "
            "notify group\. You can use the command as follows:\n\n"
            f"`/invite_to_notify_group {notify_group_name} @example_username1 "
            "@example_username2`",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return ConversationHandler.END

    # Get corresponding notify group from db
    notify_group = DBConnection().find_one(
        "notifygroups",
        {"chat_id": chat_id, "name": notify_group_name}
    )

    # Cancel command if the notify group doesn't exist
    if not notify_group:
        update.message.reply_text(
            "A notify group with that name does not exist\.",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return ConversationHandler.END
    
    creator_mention = get_one_mention(
        context.bot, notify_group["creator_id"], chat_id
    )

    # Cancel command if the user who is inviting is not the creator of the 
    # notify group
    if notify_group["creator_id"] != user_id:
        send_loud_and_silent_message(
            context.bot,
            "Processing\.\.\.",
            "Sorry, you can not invite people to the notify group as only the "
            f"creator of the notify group \({creator_mention}\) can invite "
            "people",
            chat_id,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return ConversationHandler.END

    # Ensure that the people who are being invited are not already a part of
    # the notify group.
    # Get the usernames of all the members in the notify groups.
    notify_group_member_usernames = set(
        [f"@{get_user(context.bot, member_id, chat_id).username}"
         for member_id in notify_group["members"]]
    )

    # Get the list of the invited users to save in the database later AND to
    # tag them for the invitation
    invited_users_identifiers = set([])
    user_ids_of_members_but_also_invited = []
    for entity in update.message.entities:
        if entity.type == "text_mention":
            # Don't invite users who are already members in the notify group!
            if entity.user.id in notify_group["members"]:
                user_ids_of_members_but_also_invited.append(entity.user.id)
            else:
                invited_users_identifiers.add(entity.user.id)
        elif entity.type == "mention":
            # Get the user's username
            username = update.message.text[
                entity.offset:entity.offset+entity.length
            ]
            # Don't invite users who are already members in the notify group!
            if username in notify_group_member_usernames:
                user_ids_of_members_but_also_invited.append(username)
            else:
                invited_users_identifiers.add(username)

    # Cancel the invite if there all invited users are already members
    if not invited_users_identifiers:
        update.message.reply_text(
            "An invitation could not be sent out because the users you tried "
            "to invite are already members",
            parse_mode=ParseMode.MARKDOWN_V2,
            quote=True
        )
        return ConversationHandler.END

    invitation_id = ObjectId()

    # Update invited list of the notify group with the new invited users
    notify_group["invited"] = list(
        set(
            notify_group["invited"]
        ).union(
            invited_users_identifiers
        )
    )
    DBConnection().update_one(
        "notifygroups",
        {"_id": notify_group["_id"]},
        {
            "$set": notify_group
        }
    )

    # Send an interface to the creator of the notify group for them to see
    # who didn't get invited and for them to be able to revoke their invite
    # if needed.

    # Setup the keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} REVOKE INVITE",
                callback_data=f"revoke-invite_{notify_group['_id']}_{invitation_id}"
            )
        ]
    ]

    # Set up the interface text, mentioning all the users who didn't get
    # invited because they were already members (if they exist)
    base_invitation_manager_msg_text = (
        f"{creator_mention} An invitation has been sent out below to the "
        "requested users\."
    )
    extra_invitation_manager_msg_text = ""
    if user_ids_of_members_but_also_invited:
        mentions_of_members_but_also_invited = get_many_mentions(
            context.bot, chat_id, user_ids_of_members_but_also_invited
        )
        extra_invitation_manager_msg_text += (
            " However, the following users were not invited because they are "
            f"already members:\n{mentions_of_members_but_also_invited}"
        )

    extra_invitation_manager_msg_text += (
        "\n\nYou can revoke the invite you sent out below by clicking on the "
        "'Revoke Invite' button just under this message\.\n\n*Note \#1* "
        "Members who have already joined your notify group through this "
        "invite will still remain a member even if you revoke the invite\. "
        "You will need to use `/modify_notify_group` to remove them as a "
        "member from your notify group\.\n\n*Note \#2* If an invited member "
        "changes their username before accepting/rejecting the invite, they "
        "may need to be reinvited to accept or reject the invite"
    )

    # Finally, send the message to the creator of the notify group
    mgr_msg = send_loud_and_silent_message(
        context.bot,
        base_invitation_manager_msg_text,
        base_invitation_manager_msg_text + extra_invitation_manager_msg_text,
        chat_id,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Send an interface to the invited users of the notify group for them to
    # be able to accept or reject the invite to the notify group

    # Set up the keyboard with the accept/reject options for the notify group
    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CROSS_EMOJI} DECLINE",
                callback_data=f"decline_{notify_group['_id']}_{invitation_id}"
            ),
            InlineKeyboardButton(
                f"{values.CHECKMARK_EMOJI} ACCEPT",
                callback_data=f"accept_{notify_group['_id']}_{invitation_id}"
            )
        ]
    ]

    # Get the user mentions of all the users who were invited
    user_mentions_str = get_many_mentions(
        context.bot, chat_id, invited_users_identifiers, " "
    )

    # Send the message to the invited users for the notify group
    inv_msg = send_loud_and_silent_message(
        context.bot,
        user_mentions_str,
        f"{user_mentions_str} You have been invited to the "
        f"`{notify_group_name}` notify group\. Below are the details of this "
        "group\. You can choose to either accept this invite so you will be "
        f"notified everytime someone does `/notify {notify_group_name}` or "
        "you can choose to decline\n\n"
        f"{stringify_notify_group(context.bot, notify_group)}",
        chat_id,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.chat_data[f"{invitation_id}"] = {
        "actively_invited": invited_users_identifiers,
        "initially_invited": invited_users_identifiers.copy(),
        "inv_msg": inv_msg,
        "mgr_msg": mgr_msg
    }

    return WAITING_FOR_REPLY


def reply_to_invite(update, context):
    """
    Registers response from the invited members to the notify group invitation
    """
    update = update.callback_query
    update.answer()
    reply, notify_group_id, invitation_id = update.data.split("_")
    curr_user_id = update.from_user.id
    chat_id = update.message.chat.id
    curr_username = (f"@{update.from_user.username}"
                     if update.from_user.username else None)
    notify_group_invitation = context.chat_data[invitation_id]
    
    # Let the user know we are processing their request.
    notify_group_invitation["inv_msg"].edit_text(
        "Processing\.\.\.",
        parse_mode=ParseMode.MARKDOWN_V2
    )

    # Get the notify group from the notify group id
    notify_group = DBConnection().find_one(
        "notifygroups",
        {"_id": ObjectId(notify_group_id)}
    )

    # Silently cancel command if the notify group doesn't exist anymore
    if not notify_group:
        # Remove the invites data for that notify group
        context.chat_data[invitation_id]["mgr_msg"].delete()
        context.chat_data[invitation_id]["inv_msg"].edit_text(
            "The notify group whose invitation you are trying to respond to "
            "does not exist anymore",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        context.chat_data.pop(invitation_id)
        return ConversationHandler.END

    # Remove users who were in the invited list and stop any users who are not
    # in the invited list
    if curr_user_id in notify_group["invited"]:
        notify_group["invited"].remove(curr_user_id)
        if curr_user_id in notify_group_invitation["actively_invited"]:
            notify_group_invitation["actively_invited"].remove(curr_user_id)   
    elif curr_username and curr_username in notify_group["invited"]:
        notify_group["invited"].remove(curr_username)
        if curr_username in notify_group_invitation["actively_invited"]:
            notify_group_invitation["actively_invited"].remove(curr_username)   
    else:
        return WAITING_FOR_REPLY

    # At this point, anybody who wasn't invited to the closed group has been
    # booted.

    # If the user reply is accept and user doesn't exist in the members list,
    # add the user id to the members list
    if reply == "accept" and not curr_user_id in notify_group["members"]:
        # Update members list with the current user id
        notify_group["members"].append(curr_user_id)

    # Save invited users and maybe member changes in the db
    DBConnection().update_one(
        "notifygroups",
        {"_id": notify_group["_id"]},
        {
            "$set": notify_group
        }
    )

    # Get the users mentions for the updated invited members
    invited_members_mentions_str = get_many_mentions(
        context.bot, chat_id, notify_group_invitation["initially_invited"], " "
    )
    if not notify_group_invitation["actively_invited"]:
        creator_mention = get_one_mention(
            context.bot, notify_group["creator_id"], chat_id
        )
        notify_group_invitation["mgr_msg"].edit_text(
            f"{creator_mention} The invited users have successfully responded "
            "to the invite so you can no longer revoke the invitation\. You "
            f"can however use the `/modify_notify_group` command in this "
            "group chat to remove any members from your notify group",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        notify_group_invitation["inv_msg"].edit_text(
            f"{invited_members_mentions_str} You have successfully responded "
            f"to the invitation to `{notify_group['name']}` notify group sent "
            f"out by {creator_mention}\. Below are the details of this notify "
            f"group:\n\n{stringify_notify_group(context.bot, notify_group)}",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        # End the conversation if there are no more invited users
        context.chat_data.pop(invitation_id)
        return ConversationHandler.END

    # Set up the keyboard with the accept/reject options for the notify group
    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CROSS_EMOJI} DECLINE",
                callback_data=f"decline_{notify_group_id}_{invitation_id}"
            ),
            InlineKeyboardButton(
                f"{values.CHECKMARK_EMOJI} ACCEPT",
                callback_data=f"accept_{notify_group_id}_{invitation_id}"
            )
        ]
    ]

    # Update the interface for the invited users with the updated invited
    # members
    notify_group_invitation["inv_msg"].edit_text(
        f"{invited_members_mentions_str} You have been invited to the "
        f"`{notify_group['name']}` notify group\. Below are the details "
        "of this group\. You can choose to either accept this invite so "
        "you will be notified everytime someone does `/notify "
        f"{notify_group['name']}`, or you can choose to decline\n\n"
        f"{stringify_notify_group(context.bot, notify_group)}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    # Keep listening for other users to accept/reject
    return WAITING_FOR_REPLY


def revoke_invitation(update, context):
    """
    This handler will revoke any invitations sent out by the creator of the
    notify group corresponding to the notify group id in the callback data
    """
    update = update.callback_query
    update.answer()
    _, notify_group_id, invitation_id = update.data.split("_")
    curr_user_id = update.from_user.id
    chat_id = update.message.chat.id

    # Grab the notify group from the db
    notify_group = DBConnection().find_one(
        "notifygroups",
        {"_id": ObjectId(notify_group_id)}
    )
    notify_group_invitation = context.chat_data[invitation_id]

    # Cancel command if the notify group has been deleted
    if not notify_group:
        notify_group_invitation["mgr_msg"].delete()
        notify_group_invitation["inv_msg"].edit_text(
            "The notify group whose invitation you are trying to respond to "
            "does not exist anymore",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        context.chat_data.pop(invitation_id)
        return ConversationHandler.END
    
    # Ignore request if current user is not the creator of the notify group
    if notify_group["creator_id"] != curr_user_id:
        return WAITING_FOR_REPLY

    # Get the initially invited users and remove them from the invited list
    notify_group["invited"] = list(
        set(
            notify_group["invited"]
        ).difference(
            notify_group_invitation["initially_invited"]
        )
    )

    # Remove all invited users from the invite
    DBConnection().update_one(
        "notify_group",
        {"_id": notify_group["_id"]},
        {
            "$set": notify_group
        }
    )

    # Get the mention for the creator and the interfaces messages 
    creator_mention = get_one_mention(
        context.bot, notify_group["creator_id"], chat_id
    )

    # Update the interfaces for both the creator and invited users.
    notify_group_invitation["mgr_msg"].edit_text(
        f"{creator_mention}\n\n{values.CANCELLED_EMOJI} You have "
        f"successfully revoked the invite to the `{notify_group['name']}` "
        "notify group",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    notify_group_invitation["inv_msg"].delete()
    context.chat_data.pop(invitation_id)

    # End the conversation
    return ConversationHandler.END
