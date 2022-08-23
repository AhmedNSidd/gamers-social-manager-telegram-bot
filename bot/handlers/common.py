from general import strings
from telegram.ext import ConversationHandler


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
