from general import strings
from telegram import Bot, Message
from telegram.ext import ConversationHandler
from telegram.utils.helpers import mention_markdown, escape_markdown


def cancel_current_conversation(update, context, running_command_name):
    """
    This function will stop any running conversation and delete all stored
    messages meant to be deleted. 
    """
    # Delete all old messages that are meant to be deleted
    while len(context.user_data["messages_to_delete"]):
        old_message = context.user_data["messages_to_delete"].pop()
        old_message.delete()

    # Send a message to the user that we are cancelling the current
    # conversation
    update.message.reply_text(
        strings.cancel_command_due_to_new_command.format(running_command_name),
        quote=True
    )
    return ConversationHandler.END


def get_user(bot: Bot, user_id: int, chat_id: int):
    user = bot.get_chat_member(chat_id, user_id).user
    return user


def get_one_mention(bot: Bot, user_id: int, chat_id: int):
    """
    This function returns a Markdown link to a user's profile given that the
    bot is in the same chat as them.
    """
    user = get_user(bot, user_id, chat_id)
    user_label = (f"@{user['username']}" if user.username
                  else f"{user['first_name']}")

    return mention_markdown(user_id, user_label, 2)


def get_many_mentions(bot: Bot, chat_id: int, user_identifiers: list, separator="\n"):
    user_mentions_str = ""
    for invited_member_identifier in user_identifiers:
        if type(invited_member_identifier) == str:
            # The identifier is a username
            escaped_username = escape_markdown(invited_member_identifier, 2)
            user_mentions_str += f"{escaped_username}{separator}"
        else:
            # The identifier is a telegram ID
            user_mention = get_one_mention(
                bot, invited_member_identifier, chat_id
            )
            user_mentions_str += f"{user_mention}{separator}"
    if user_mentions_str:
        user_mentions_str = user_mentions_str[:-1]  # Remove the last space

    return user_mentions_str


def send_loud_and_silent_message(bot: Bot, initial_text: str, final_text: str, chat_id: int, **msg_kwargs) -> Message:
    """
    This function is used to send a message with initial text that will notify
    other users if they are tagged in the initial text. The bot will then edit
    that message with the final text. If any users are tagged in the final_text
    they will not be notified.
    """
    # Send a message that will be loud. If other users are tagged here, they
    # will be notified
    message = bot.send_message(
        chat_id, initial_text, **msg_kwargs
    )

    # Edit the loud message with the final text. If users are tagged here, they
    # will not be notified
    return message.edit_text(final_text, **msg_kwargs)
