from telegram import Bot
from handlers.common import get_one_mention


def stringify_status_user(bot: Bot, status_user: dict):
    """
    Given a dictionary that contains fields of a status user, this function
    will return a formatted string message that displays this status user
    """
    display_name = status_user.get("display_name")
    creator_mention = get_one_mention(
        bot, status_user["user_id"], status_user["chat_id"]
    )
    creator_details = (
        f"{creator_mention} in the `{status_user['group_name']}` group chat"
        if status_user.get('group_name')
        else f"{creator_mention} in this private chat"
    )
    xbox_gamertag = status_user.get("xbox_gamertag")
    psn_online_id = status_user.get("psn_online_id")

    return (
        f"`{display_name}` \| _Created by {creator_details}_\n"
        "__Xbox Gamertag__\n"
        f"`{xbox_gamertag}`\n"
        "__PSN Online ID__\n"
        f"`{psn_online_id}`"
    )
