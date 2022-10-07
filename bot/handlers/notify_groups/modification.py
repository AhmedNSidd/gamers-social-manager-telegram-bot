from bson.objectid import ObjectId
from handlers.notify_groups.common import stringify_notify_group
from handlers.common import get_many_mentions, get_one_mention_using_user, \
                            get_one_mention, get_user, get_user_label, \
                            escape_text
from general import values, strings, inline_keyboards
from general.db import DBConnection
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler
from telegram.error import Unauthorized


# Conversation stats for the CommandHandler for modify_notify_group
MAIN_MENU, EDITING_NOTIFY_GROUP_NAME, EDITING_NOTIFY_GROUP_DESCRIPTION, \
    EDITING_NOTIFY_GROUP_MEMBERS, REVOKE_NOTIFY_GROUP_INVITE, \
        DELETING_NOTIFY_GROUP = range(6)


def start(update, context):
    """
    This handler will serve as the start of a conversation with the user on
    which NotifyGroups they would like to modify.
    """
    is_callback = False
    # The entry points are:
    # a) if someone presses the back button in which case we shouldn't
    # recollect
    # b) if a fresh command is entered in the group chat in which case info 
    # should be collected but promptly the convo should be ended
    # c) if the conversation is started using a button in which case, essential
    # info should be collected
    if update.callback_query:
        # It could only be a callback if the process was started via a button
        # in the private chat regarding a group chat (in which case we need to
        # collect fresh essential information), or if the interface already
        # existed and the user pressed `back` in which case we shouldn't
        # collect information again
        is_callback = True
        update = update.callback_query
        update.answer()
        callback_data_tokens = update.data.split("_")
        if len(callback_data_tokens) != 3:
            # It is three tokens if the `back` button was pressed
            # Else, we are dealing with the start of a modify status user
            # process for a group chat in the private chat
            context.user_data["user_id"] = update.message.chat.id
            group_chat_id = callback_data_tokens[1]
            group_chat = context.bot.get_chat(group_chat_id)
            context.user_data["chat_id"] = group_chat.id
            context.user_data["group_name"] = group_chat.title
    else: 
        # Collect the essential information for the command that was entered.
        # This could happen if /modify_status_user was entered in a group chat
        # If it's a private chat, an error should be entered.
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

    context.user_data["user_mention"] = get_one_mention(
        context.bot, context.user_data["user_id"], context.user_data["chat_id"]
    )

    if not is_callback and context.user_data["group_name"]:
        # If we're in a group, then just send a private button to start
        # the process and end this current conversation
        escaped_group_name = escape_text(context.user_data['group_name'])
        try:
            context.bot.send_message(
                context.user_data["user_id"],
                strings.CLICK_BUTTON_TO_START_PROCESS(
                    f"modifying a notify group for the _{escaped_group_name}_ "
                    "group chat"
                ),
                reply_markup=inline_keyboards.mng_start_keyboard(
                    context.user_data["chat_id"]
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except Unauthorized:
            # send a group message that the bot was unable to send a
            # private message if there's an error
            update.message.reply_text(
                strings.BOT_UNABLE_TO_SEND_PRIVATE_MESSAGE(
                    context.user_data["user_mention"],
                    "modifying a notify group",
                    "/modify\_notify\_group"
                ),
                reply_markup=inline_keyboards.go_to_private_chat_keyboard(
                    context.bot.get_me().username,
                    f"mng_{context.user_data['chat_id']}"
                ),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            # send a group message that the bot sent a private message to
            # modify a status user
            update.message.reply_text(
                strings.BOT_SENT_A_PRIVATE_MESSAGE(
                    context.user_data["user_mention"],
                    "to modify a notify group for this group chat"
                ),
                reply_markup=inline_keyboards.go_to_private_chat_keyboard(
                    context.bot.get_me().username,
                ),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        finally:
            return ConversationHandler.END

    user_group_privilege = context.bot.get_chat_member(
        context.user_data["chat_id"], context.user_data["user_id"]
    ).status

    if (user_group_privilege == "creator"
            or user_group_privilege == "administrator"):
        notify_groups_to_modify = DBConnection().find(
            "notifygroups", {"chat_id": context.user_data["chat_id"]}
        )
    else:
        notify_groups_to_modify = DBConnection().find(
            "notifygroups", {"chat_id": context.user_data["chat_id"],
                             "creator_id": context.user_data["user_id"]}
        )

    # If there are no notify groups to modify, stop the convo and let the user
    # know
    if not notify_groups_to_modify:
        if is_callback:
            update.message.edit_text(
                "You have no notify groups to modify in the "
                f"`{context.user_data['group_name']}` group chat\. Please add "
                "one first by entering `/add_notify_group` in that group chat",
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            update.message.reply_text(
                "You have no notify groups to modify\. Please add one "
                "first by entering `/add_notify_group` in this group chat",
                parse_mode=ParseMode.MARKDOWN_V2
            )
        
        return ConversationHandler.END

    my_notify_groups = {}
    other_notify_groups = {}
    for notify_group in notify_groups_to_modify:
        if notify_group["creator_id"] == context.user_data["user_id"]:
            my_notify_groups[notify_group["_id"]] = notify_group["name"]
        else:
            other_notify_groups[notify_group["_id"]] = notify_group["name"]

    if not other_notify_groups:
        notify_group_msg = (
            "Choose which notify group you want to modify in the "
            f"`{context.user_data.get('group_name')}` group chat\."
        )
    else: 
        notify_group_msg = (
            "Choose which notify group you want to modify in the "
            f"`{context.user_data.get('group_name')}` group chat\."
        )

    # Create the keyboard with all the notify groups
    keyboard = [[]]
    for id in my_notify_groups:
        if len(keyboard[-1]) < 2:
            keyboard[-1].append(InlineKeyboardButton(
                f"{my_notify_groups[id]} (Yours)", callback_data=str(id)
            ))
        else:
            keyboard.append([InlineKeyboardButton(
                f"{my_notify_groups[id]} (Yours)", callback_data=str(id)
            )])

    for id in other_notify_groups:
        if len(keyboard[-1]) < 2:
            keyboard[-1].append(InlineKeyboardButton(
                f"{other_notify_groups[id]} (Others)", callback_data=str(id)
            ))
        else:
            keyboard.append([InlineKeyboardButton(
                f"{other_notify_groups[id]} (Others)", callback_data=str(id)
            )])

    keyboard_markup = InlineKeyboardMarkup(keyboard)
    if is_callback:
        # If someone presses the "back" button to go back to the home screen 
        # of the interface
        update.message.edit_text(
            notify_group_msg,
            reply_markup=keyboard_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    else:
        # This is the case where someone just typed /modify_notify_group
        update.message.reply_text(
            notify_group_msg,
            reply_markup=keyboard_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )

    return MAIN_MENU


def edit_or_delete(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    user_id = context.user_data["user_id"]
    query_for_notify_group = {"_id": ObjectId(update.data)}
    notify_group_to_modify = DBConnection().find_one("notifygroups",
                                                     query_for_notify_group)

    context.user_data['notify_group_to_modify'] = notify_group_to_modify
    keyboard = [
        [
            InlineKeyboardButton(f"{values.CROSS_EMOJI} DELETE",
                                 callback_data=f"delete_{update.data}")
        ],
        [
            InlineKeyboardButton(f"{values.LEFT_POINTING_EMOJI} GO BACK",
                                 callback_data="modify_notify_group")
        ]
    ]
    if notify_group_to_modify["creator_id"] == user_id:
        keyboard[0].insert(0, InlineKeyboardButton(
            f"{values.PENCIL_EMOJI} EDIT", callback_data=f"edit_{update.data}"
        ))

    update.edit_message_text(
        stringify_notify_group(context.bot, notify_group_to_modify),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    return MAIN_MENU


def edit(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    user_id = context.user_data["user_id"]
    group_name = context.user_data['group_name']
    notify_group_to_edit = context.user_data["notify_group_to_modify"]
    user_mention = context.user_data["user_mention"]

    update.message.delete()
    context.user_data["messages"] = [context.bot.send_message(
        user_id,
        f"Hey {user_mention}\! We will edit your notify group "
        f"`{notify_group_to_edit['name']}`\n\nI will ask you to edit the "
        "group name, description, members in the notify group, and invites "
        "sent out for the notify group\. You can choose to skip if you would "
        "prefer not to edit these entries and leave them as they are\.\n\nYou "
        "can also choose to cancel any edits made to the notify group at any "
        "point during this process\n\n",
        parse_mode=ParseMode.MARKDOWN_V2
    )]
    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        f"Below are the details of the notify group \(in the `{group_name}` "
        "group chat\) you're editing:\n\n" +
        stringify_notify_group(context.bot, notify_group_to_edit),
        parse_mode=ParseMode.MARKDOWN_V2
    ))
    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} DISCARD EDITS",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_name"
        ),
    ]]
    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        "Enter the new *name* for your notify group \(currently set as "
        f"`{notify_group_to_edit['name']}`\)",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    ))
    return EDITING_NOTIFY_GROUP_NAME


def process_name(update, context):
    # Here we have to ensure that the name that the user has chosen is:
    # not empty, but also is unique relative to where they are trying to add it
    is_callback = False
    if update.callback_query:
        is_callback = True
        update = update.callback_query
        new_notify_group_name = update.data
        update.answer()

    chat_id = context.user_data["chat_id"]
    user_id = context.user_data["user_id"]
    escaped_group_name = escape_text(context.user_data["group_name"])
    notify_group_to_edit = context.user_data["notify_group_to_modify"]

    keyboard = [[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} DISCARD EDITS",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_name"
        ),
    ]]
    if not is_callback:
        context.user_data["messages"].append(update.message)
        new_notify_group_name = update.message.text.strip()

        if not new_notify_group_name:
            context.user_data["messages"].append(update.message.reply_text(
                "You did not provide a valid notify group name\. Please enter "
                "a unique notify group name",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_NOTIFY_GROUP_NAME
        elif new_notify_group_name == notify_group_to_edit["name"]:
            context.user_data["messages"].append(update.message.reply_text(
                "The notify group name you entered is the same as the "
                "previously set name\. Please enter a new name or skip this "
                "entry",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_NOTIFY_GROUP_NAME
        elif ' ' in new_notify_group_name:
            alt_name = "_".join(new_notify_group_name.split(" "))
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{values.STAR_EMOJI} USE ALTERNATIVE NAME",
                        callback_data=f"{alt_name}"
                    )
                ]
            )
            context.user_data["messages"].append(update.message.reply_text(
                "You can not have a space in your notify group name\. Here's "
                "an alternative notify group name that you can try instead: "
                f"`{alt_name}`\n\nPlease enter a valid notify group name",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_NOTIFY_GROUP_NAME

        notify_groups_with_the_same_name = DBConnection().count_documents(
            "notifygroups",
            {"chat_id": chat_id, "name": new_notify_group_name}
        )
        if notify_groups_with_the_same_name > 0:
            context.user_data["messages"].append(update.message.reply_text(
                "A notify group with that name already exists in the "
                f"_{escaped_group_name}_ group chat\. Please enter a unique "
                "name",
                reply_markup=InlineKeyboardButton(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2,
                quote=True
            ))
            return EDITING_NOTIFY_GROUP_NAME

    if is_callback and new_notify_group_name == "skip_name":
        ng_edit_msg = "Skipped editing your notify group name"
    else:
        ng_edit_msg = (
            f"Great\! The group name has been set as `{new_notify_group_name}`"
        )
        notify_group_to_edit["name"] = new_notify_group_name

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} DISCARD EDITS",
                callback_data=f"cancel"
            ),
            InlineKeyboardButton(
                f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
                callback_data=f"skip_description"
            ),
        ]
    ]
    while len(context.user_data["messages"]) > 2:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    context.user_data["messages"].append(context.bot.send_message(
        user_id, ng_edit_msg, parse_mode=ParseMode.MARKDOWN_V2
    ))

    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        "Enter the new *description* \(currently set as "
        f"`{notify_group_to_edit['description']}`\)",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    ))

    return EDITING_NOTIFY_GROUP_DESCRIPTION


def process_description(update, context):
    is_callback = False
    if update.callback_query:
        is_callback = True
        update = update.callback_query
        new_notify_group_description = update.data
        update.answer()

    user_id = context.user_data["user_id"]
    notify_group_to_edit = context.user_data["notify_group_to_modify"]
    chat_id = notify_group_to_edit["chat_id"]

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} DISCARD EDITS",
                callback_data=f"cancel"
            ),
            InlineKeyboardButton(
                f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
                callback_data=f"skip_description"
            ),
        ]
    ]

    if is_callback:
        description_msg = "Skipped editing your description"
    else: 
        context.user_data["messages"].append(update.message)
        new_notify_group_description = update.message.text.strip()
        if not new_notify_group_description:
            context.user_data["messages"].append(update.message.reply_text(
                "You did not provide a valid description for your notify group"
                "\. Please enter a valid description",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_NOTIFY_GROUP_DESCRIPTION
        elif new_notify_group_description == notify_group_to_edit["description"]:
            context.user_data["messages"].append(update.message.reply_text(
                "The description you entered is the same as the previously "
                "set description\. Please enter a new description or skip "
                "this entry",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
                quote=True
            ))
            return EDITING_NOTIFY_GROUP_DESCRIPTION

        notify_group_to_edit["description"] = new_notify_group_description
        description_msg = ("Great\! Your description has been set as:\n\n"
                           f"`{new_notify_group_description}`")

    while len(context.user_data["messages"]) > 3:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    # Set up the interface to edit the notify group's members.
    # The interface needs the following button options:
    # - EDIT OTHER MEMBERS | ADD YOURSELF/REMOVE YOURSELF
    # - DISCARD ALL EDITS | SKIP ENTRY
    # - CONFIRM CHANGES TO MEMBERS/None
    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.PENCIL_EMOJI} EDIT OTHER MEMBERS",
                callback_data=f"edit_other_members"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} DISCARD EDITS",
                callback_data=f"cancel"
            ),
            InlineKeyboardButton(
                f"{values.NEXT_TRACK_EMOJI} SKIP ENTRY",
                callback_data=f"skip_members"
            ),
        ]
    ]

    if notify_group_to_edit["creator_id"] in notify_group_to_edit["members"]:
        keyboard[0].append(
            InlineKeyboardButton(
                f"{values.MINUS_EMOJI} REMOVE YOURSELF",
                # callback_data="remove_yourself_from_members"
                callback_data=f"remove_from_members_{notify_group_to_edit['creator_id']}"
            )
        )
    else:
        keyboard[0].append(
            InlineKeyboardButton(
                f"{values.PLUS_EMOJI} ADD YOURSELF",
                # callback_data="add_yourself_to_members"
                callback_data=f"add_to_members_{notify_group_to_edit['creator_id']}"
            )
        )

    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        description_msg,
        parse_mode=ParseMode.MARKDOWN_V2
    ))
    # Set up variables for members processing
    context.user_data["members_to_add"] = {}
    context.user_data["members_to_remove"] = {}
    context.user_data["members"] = {
        k:get_user(context.bot, k, chat_id) for k in 
                                                notify_group_to_edit["members"]
    }
    
    context.user_data["messages"].append(context.bot.send_message(
        user_id,
        "Below are the list of members in your notify group\. You can choose "
        "to remove other members, add or remove yourself from the members "
        "list, discard any modifications made thus far, or skip this entry\n\n"
        "*Members List:*\n" + stringify_editing_members_str(context),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    ))

    return EDITING_NOTIFY_GROUP_MEMBERS


def process_members(update, context):
    if update.callback_query:
        update = update.callback_query
        user_choice = update.data
        update.answer()

    # We aren't going to get text responses from the user, it'll be mostly
    # buttons. We need two seperate user data lists, one list will correspond
    # to the members to add, one will be for members to delete.

    # group_name = context.user_data["group_name"]
    user_id = context.user_data.get("user_id")
    edited_notify_group = context.user_data.get("notify_group_to_modify")
    chat_id = edited_notify_group["chat_id"]
    creator_id = edited_notify_group["creator_id"]

    if user_choice == "skip_members" or user_choice == "save_members":
        # Just save the rest of the changes if there are any and end the convo
        # Update the database with the changes (may or may not be any)
        # Remove old user prompts
        while len(context.user_data["messages"]) > 4:
            old_message = context.user_data["messages"].pop()
            old_message.delete()

        if user_choice == "save_members":
            edited_notify_group["members"] = list(
                (set(edited_notify_group["members"]).difference(
                    {id for id in context.user_data["members_to_remove"]}
                )
                ).union(
                    {id for id in context.user_data["members_to_add"]}
                )
            )
            
            # Send a message to the user telling them they skipped the members
            # entry without making any changes
            members_to_add_mentions = get_many_mentions(
                context.bot, chat_id, context.user_data["members_to_add"]
            )
            members_to_remove_mentions = get_many_mentions(
                context.bot, chat_id, context.user_data["members_to_remove"]
            )
            context.bot.send_message(
                user_id,
                "Saved the changes to the members list\.\n\nAdded:\n"
                f"{members_to_add_mentions}\n\nRemoved:\n"
                f"{members_to_remove_mentions}",
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            # Send a message to the user telling them they skipped the members
            # entry without making any changes
            context.bot.send_message(
                user_id,
                "Skipped editing the notify group's members list without "
                "making any changes",
                parse_mode=ParseMode.MARKDOWN_V2
            )

        DBConnection().update_one(
            "notifygroups",
            {"_id": edited_notify_group["_id"]},
            {
                "$set": edited_notify_group
            }
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    f"{values.LEFT_POINTING_EMOJI} GO BACK TO MENU",
                    callback_data=f"{edited_notify_group['_id']}"
                )
            ]
        ]

        # Then send a message giving them the updated notify group details
        context.bot.send_message(
            user_id,
            "*You've successfully updated your notify group\.* Below are the "
            "details of the notify group:\n\n" +
            stringify_notify_group(context.bot, edited_notify_group),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        # End the conversation
        return MAIN_MENU
    elif user_choice == "edit_other_members":
        # If we are choosing to edit other members, update the interface to
        # list all the members of the notify group as buttons
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{values.LEFT_POINTING_EMOJI} BACK TO MEMBERS MENU",
                    callback_data=f"members_menu"
                )
            ], 
            []
        ]
        for member_id in edited_notify_group["members"]:
            if member_id == creator_id:
                continue
            user = context.user_data["members"][member_id]
            user_label = get_user_label(user)
            if member_id in context.user_data["members_to_add"]:
                button = InlineKeyboardButton(
                    f"REMOVE {user_label}",
                    callback_data=f"remove_from_members_{member_id}"
                )
            elif member_id in context.user_data["members_to_remove"]:
                button = InlineKeyboardButton(
                    f"ADD {user_label}",
                    callback_data=f"add_to_members_{member_id}"
                )
            elif member_id in context.user_data["members"]:
                button = InlineKeyboardButton(
                    f"REMOVE {user_label}",
                    callback_data=f"remove_from_members_{member_id}"
                )
            else:
                button = InlineKeyboardButton(
                    f"ADD {user_label}",
                    callback_data=f"add_to_members_{member_id}"
                )

            if len(keyboard[-1]) < 2:
                keyboard[-1].append(button)
            else:
                keyboard.append([button])

        if len(keyboard[1]) > 0:
            context.user_data["messages"][-1].edit_text(
                "Click on a button below to remove or add *OTHER* existing "
                "members in the notify group:\n\n*Members List*\n" +
                stringify_editing_members_str(context),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            context.user_data["messages"][-1].edit_text(
                "*You don't have any other existing members in the notify "
                "group to add or remove*\n\n*Members List*\n" + 
                stringify_editing_members_str(context),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        return EDITING_NOTIFY_GROUP_MEMBERS
    
    if user_choice.startswith("add_to_members"):
        member_id_to_add = int(user_choice.split("_")[3])
        if member_id_to_add in edited_notify_group["members"]:
            # If already in members, make sure we aren't removing it
            context.user_data["members_to_remove"].pop(member_id_to_add)
        else:
            # If not already in members, make sure we are adding it.
            context.user_data["members_to_add"][member_id_to_add] = get_user(
                context.bot, member_id_to_add, chat_id
            )
    elif user_choice.startswith("remove_from_members"):
        member_id_to_remove = int(user_choice.split("_")[3])
        if member_id_to_remove in edited_notify_group["members"]:
            # If already in members, make sure we are removing it
            context.user_data["members_to_remove"][member_id_to_remove] = (
                context.user_data["members"][member_id_to_remove]
            )
        else:
            # If not in members, make sure we are not adding it
            context.user_data["members_to_add"].pop(member_id_to_remove)
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.PENCIL_EMOJI} EDIT OTHER MEMBERS",
                callback_data=f"edit_other_members"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{values.CANCELLED_EMOJI} DISCARD EDITS",
                callback_data=f"cancel"
            ),
            InlineKeyboardButton(
                f"{values.NEXT_TRACK_EMOJI} SKIP ENTRY",
                callback_data=f"skip_members"
            ),
        ]
    ]
    if ((creator_id in context.user_data["members"] and 
         creator_id not in context.user_data["members_to_remove"]
        ) or creator_id in context.user_data["members_to_add"]):
        keyboard[0].append(
            InlineKeyboardButton(
                f"{values.MINUS_EMOJI} REMOVE YOURSELF",
                # callback_data="remove_yourself_from_members"
                callback_data=f"remove_from_members_{creator_id}"
            )
        )
    else:
        keyboard[0].append(
            InlineKeyboardButton(
                f"{values.PLUS_EMOJI} ADD YOURSELF",
                # callback_data="add_yourself_to_members"
                callback_data=f"add_to_members_{creator_id}"
            )
        )
    if (context.user_data["members_to_add"] or
        context.user_data["members_to_remove"]):
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{values.CHECKMARK_EMOJI} CONFIRM CHANGES TO MEMBERS",
                    callback_data="save_members"
                )
            ]
        )

    context.user_data["messages"][-1].edit_text(
        "Editing the members of the notify group\. You can now choose to "
        "remove other members, add or remove yourself from the members list, "
        "discard any modifications made thus far, or skip this entry\n\n"
        "*Members List:*\n" + stringify_editing_members_str(context),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return EDITING_NOTIFY_GROUP_MEMBERS


def delete(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    group_name = context.user_data["group_name"]
    notify_group_to_delete = context.user_data["notify_group_to_modify"]

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK",
                callback_data=f"{notify_group_to_delete['_id']}"
            ),
            InlineKeyboardButton(
                f"{values.CHECKMARK_EMOJI} CONFIRM",
                callback_data=f"confirm_delete_{notify_group_to_delete['_id']}"
            )
        ]
    ]

    notify_group_deletion_msg = (
        "Confirm deletion of the notify group "
        f"`{notify_group_to_delete['name']}` in the `{group_name}` group chat"
    )

    update.edit_message_text(
        notify_group_deletion_msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    return DELETING_NOTIFY_GROUP


def confirm_delete(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    group_name = context.user_data["group_name"]
    notify_group_to_delete = context.user_data["notify_group_to_modify"]

    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK TO NOTIFY GROUPS",
                callback_data=f"modify_notify_group"
            ),
        ]
    ]

    DBConnection().delete_one(
        "notifygroups",
        {"_id": ObjectId(notify_group_to_delete['_id'])}
    )

    context.bot.send_message(
        context.user_data["chat_id"],
        f"`{notify_group_to_delete['name']}` has been removed as a notify "
        f"group from this group chat by {context.user_data['user_mention']}",
        parse_mode=ParseMode.MARKDOWN_V2
    )

    update.edit_message_text(
        f"Deleted `{notify_group_to_delete['name']}` from the `{group_name}` "
        "group chat",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    return MAIN_MENU


def cancel(update, context):
    if update.callback_query:
        update = update.callback_query
        update.answer()

    user_id = context.user_data.get("user_id")
    notify_group_to_edit = context.user_data.get("notify_group_to_modify")
    keyboard = [
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK TO MENU",
                callback_data=f"{notify_group_to_edit['_id']}"
            )
        ]
    ]
    while context.user_data["messages"]:
        old_message = context.user_data["messages"].pop()
        old_message.delete()

    context.bot.send_message(
        user_id,
        f"{values.CANCELLED_EMOJI} Cancelled the process of editing your "
        "notify group",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


## HELPER METHODS
def stringify_editing_members_str(context):
    s = ""
    for member_id in context.user_data["members_to_add"]:
        user = context.user_data['members_to_add'][member_id]
        s += f"{values.PLUS_EMOJI} {get_one_mention_using_user(user)}\n"

    for member_id in context.user_data["members_to_remove"]:
        user = context.user_data['members_to_remove'][member_id]
        s += f"{values.CROSS_EMOJI} ~{get_one_mention_using_user(user)}~\n"

    for member_id in context.user_data["members"]:
        if member_id not in context.user_data["members_to_remove"]:
            user = context.user_data['members'][member_id]
            s += f"{values.USER_EMOJI} {get_one_mention_using_user(user)}\n"
    return s if s else "`None`"
