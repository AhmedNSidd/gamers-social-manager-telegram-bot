from general import values
from general.db import DBConnection, SELECT_WHERE, INSERT
from general.utils import create_sql_array, get_stringized_sql_value
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler


# Conversation states for the CommandHandler for add_status_user
TYPING_NAME, TYPING_DESCRIPTION, CHOOSING_JOINING_POLICY = range(3)

def start(update, context):
    """
    Sends a private message to the user starting the add_notify_group process
    and asking for the group name
    """
    context.user_data["user_id"] = update.message.from_user.id
    context.user_data["chat_id"] = update.message.chat.id
    context.user_data["group_name"] = (
        update.message.chat.title
        if context.user_data["chat_id"] != context.user_data["user_id"]
        else None
    )
    if not context.user_data["group_name"]:
        update.message.reply_text(
            "You can only run this command in a group",
            quote=True
        )
        return ConversationHandler.END


    context.user_data["messages"] = []
    # If process was started in a group, send a group message that the bot
    # sent a private message
    keyboard = [[
        InlineKeyboardButton(
            f"{values.RIGHT_POINTING_EMOJI} GO TO PRIVATE CHAT",
            url=f"{values.BOT_URL}"
        ),
    ]]
    update.message.reply_text(
        f"Hey {update.message.from_user.first_name}!\n\nI have sent you "
        "a private message which you can respond to to add a notify group to "
        "this group",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
    ]]
    context.user_data["messages"].append(context.bot.send_message(
        context.user_data["user_id"],
        f"Hey {update.message.from_user.first_name}!\n\nWe will add a notify "
        f"group to the _{context.user_data['group_name']}_ group.\n\nI will "
        "ask you for the name, description, and whether you want the "
        "group to be open or invite only.\n\nYou can choose to cancel the "
        "process of adding this notify group at any point during this process",
        parse_mode=ParseMode.MARKDOWN
    ))
    context.user_data["messages"].append(context.bot.send_message(
        context.user_data["user_id"], 
        "Enter the *name* for the notify group you want to add to the " 
        f"_{context.user_data['group_name']}_ group e.g. _Weeknight Gamers_",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    ))
    return TYPING_NAME

def process_name(update, context):
    name = update.message.text.strip()
    chat_id = context.user_data.get("chat_id")
    context.user_data["messages"].append(update.message)
    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
    ]]
    if not name:
        # If the notify group name is empty, then send an error message.
        context.user_data["messages"].append(update.message.reply_text(
            "You did not provide a valid notify group name. Please enter a "
            "valid notify group name", quote=True
        ))
        return TYPING_NAME
    
    # Check if an existing display name is present in the group/private chat.
    name_exists = DBConnection().fetchone(
        SELECT_WHERE.format(
            "1", "NotifyGroups",
            f"telegramChatID = {chat_id} AND name = '{name}'"
        )
    )
    if name_exists:
        context.user_data["messages"].append(update.message.reply_text(
            "A notify group with that name already exists in the "
            f"_{context.user_data['group_name']}_ group. Please enter a " 
            "unique notify group name",
            parse_mode=ParseMode.MARKDOWN,
            quote=True
        ))
        return TYPING_NAME

    # if we've gotten here, it means the group name is unique.
    context.user_data["name"] = name
    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_description"
        )
    ]]
    while len(context.user_data["messages"]) > 1:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    context.user_data["messages"].append(context.bot.send_message(
        context.user_data.get("user_id"),
        f"Great! The notify group name has been set as *{name}*",
        parse_mode=ParseMode.MARKDOWN
    ))

    context.user_data["messages"].append(context.bot.send_message(
        context.user_data.get("user_id"),
        "Enter the **description** for the notify group you want to add "
        f"to _{context.user_data['group_name']}_ group e.g. _This group plays "
        "games every weeknight_",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    ))
    return TYPING_DESCRIPTION

def process_description(update, context):
    is_callback = False
    if update.callback_query:
        is_callback = True
        update = update.callback_query
        description = update.data
        update.answer()

    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_description"
        )
    ]]

    if not is_callback:
        context.user_data["messages"].append(update.message)
        description = update.message.text.strip()
        if not description:
            # If the group description is empty, then send an error message.
            context.user_data["messages"].append(update.message.reply_text(
                "You did not provide a valid description. Please enter a "
                "valid description", quote=True
            ))
            return TYPING_DESCRIPTION

    if is_callback and description == "skip_description":
        status_msg_prefix = "Skipped entry of description\n\n"
    else:
        context.user_data["description"] = description
        status_msg_prefix = ("Great\! The group description has been set as "
                             f"`{description}`")

    while len(context.user_data["messages"]) > 2:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.UNLOCKED_EMOJI} OPEN",
                callback_data="Open_joining_policy"
            ),
            InlineKeyboardButton(
                f"{values.LOCKED_EMOJI} INVITE ONLY",
                callback_data="InviteOnly_joining_policy"
            )
        ],
        [
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} CANCEL",
                callback_data=f"cancel"
            )
        ],
    ]
    context.user_data["messages"].append(context.bot.send_message(
        context.user_data.get("user_id"),
        status_msg_prefix,
        parse_mode=ParseMode.MARKDOWN_V2
    ))
    context.user_data["messages"].append(context.bot.send_message(
        context.user_data.get("user_id"),
        "Choose whether you want this group to be either:\n\n"
        f"- Open (anybody in the _{context.user_data['group_name']}_ group "
        "can join this notify group)\n- Invite Only (only the members in the "
        f"_{context.user_data['group_name']}_ group that you choose to invite "
        "can join this notify group)",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    ))
    return CHOOSING_JOINING_POLICY

def process_joining_policy(update, context):
    update = update.callback_query
    username = (update.from_user['username'] if update.from_user['username']
                else update.from_user['first_name'])
    joining_policy = update.data.split("_")[0]
    update.answer()

    context.user_data["joining_policy"] = joining_policy

    while len(context.user_data["messages"]) > 3:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    ret = process_new_notify_group(context)
    if type(ret) == int:
        return ret

    mention = f"[{username}](tg://user?id={context.user_data['user_id']})"
    context.bot.send_message(
        context.user_data.get("chat_id"),
        f"*{context.user_data['name']}* has been added as a notify "
        f"group by {mention}",
        parse_mode=ParseMode.MARKDOWN
    )

    context.bot.send_message(
        context.user_data["user_id"],
        "Great! The group's joining policy has been set as "
        f"*{joining_policy}*",
        parse_mode=ParseMode.MARKDOWN
    )

    context.bot.send_message(
        context.user_data["user_id"],
        f"*You've successfully added a new notify group\.* Below are the "
        "details of the new notify group:\n\n"
        "__Group Name__\n"
        f"`{context.user_data['name']}`\n\n"
        "__Group Description__\n"
        f"`{context.user_data.get('group_description')}`\n\n"
        "__Group Joining Policy__\n"
        f"`{context.user_data['joining_policy']}`\n\n"
        "__Current Members__\n"
        f"None\. You can use `/invite_to_notify_group "
        f"{context.user_data['name']} [tag all the users you want to "
        f"invite to the group]` in the _{context.user_data['group_name']}_ "
        "group to invite group members to the notify group\n\n"
        "__Creator__\n"
        f"Added by {mention} in the _{context.user_data['group_name']}_ group",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    context.user_data.clear()
    return ConversationHandler.END

def process_new_notify_group(context):
    user_id = context.user_data.get("user_id")
    chat_id = context.user_data.get("chat_id")

    name = get_stringized_sql_value(
        context.user_data.get("name")
    )
    description = get_stringized_sql_value(
        context.user_data.get("description")
    )
    invite_only = context.user_data.get("joining_policy") == "InviteOnly"
    
    DBConnection().execute(INSERT.format(
        "NotifyGroups (telegramChatID, creatorID, name, description, "
        "inviteOnly, members)",
        f"({chat_id}, {user_id}, {name}, {description}, {invite_only}, "
        f"{create_sql_array([user_id])})"
    ))

def cancel(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    while context.user_data["messages"]:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    context.bot.send_message(
        context.user_data["user_id"],
        f"{values.CANCELLED_EMOJI} Cancelled the process of adding a notify "
        "group"
    )
    context.user_data.clear()
    return ConversationHandler.END

def stop_cmds(update, context):
    context.user_data["messages"].append(update.message)
    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
    ]]
    context.user_data["messages"].append(update.message.reply_text(
        "All commands have been blocked until you finish the add notify "
        "group process, or choose to cancel to process",
        reply_markup=InlineKeyboardMarkup(keyboard),
        quote=True
    ))