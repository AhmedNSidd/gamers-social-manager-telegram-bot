from telegram import Bot
from telegram.utils.helpers import escape_markdown
from handlers.common import get_one_mention


def stringify_notify_group(bot: Bot, notify_group: dict):
    """
    Given a dictionary that contains fields of a notify group, this function
    will return a formatted string message that displays this notify group.
    """
    # Get the creator label
    creator_mention = get_one_mention(
        bot, notify_group['creator_id'], notify_group['chat_id']
    )
    notify_group_name = escape_markdown(notify_group["name"], 2)

    notify_group_description = (escape_markdown(notify_group["description"], 2)
                                if notify_group["description"] else "None")

    # Add group name and group description
    s = (
        f"*{notify_group_name}* _\(Created by {creator_mention}\)_\n"
        "__Group Description__\n"
        f"`{notify_group_description}`\n"
        "__Current Members__\n"
    )
    # Add current members
    if notify_group["members"]:
        for member_id in notify_group["members"]:
            if member_id == notify_group["creator_id"]:
                s += f"{creator_mention}\n"
                continue
            # TODO (#40): Check for error here, the member could have left the
            # chat group.
            s += f"{get_one_mention(bot, member_id, notify_group['chat_id'])}\n"
    else:
        s += "`None`"

    # Add current invited users
    s += "__Invited Users__\n"
    if notify_group["invited"]:
        for invited_user_identifier in notify_group["invited"]:
            if type(invited_user_identifier) == str:
                s += f"{invited_user_identifier}\n"
            else:
                s += f"{get_one_mention(bot, invited_user_identifier, notify_group['chat_id'])}\n"
    else:
        s += "`None`"
    return s
