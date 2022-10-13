import logging

from bson import ObjectId
from handlers.common import escape_text
from general import db, inline_keyboards, strings, values
from telegram import Bot, ParseMode, LabeledPrice
from telegram.error import Unauthorized
from telegram.ext import ConversationHandler
from telegram.utils.helpers import create_deep_linked_url

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Conversation state for the help menu 
HELP_MENU = 0

# Conversation state for the announcement command
AWAITING_CONFIRMATION = 0

def about(update, context):
    bot_version_escaped_str = escape_text(values.BOT_VERSION.__str__())
    update.message.reply_text(
        f"Gamers Utility Bot v{bot_version_escaped_str}\n"
        "_Created by [Ahmed Siddiqui](https://github.com/AhmedNSidd/)_\n\n"
        "This is a Telegram bot created to give gamers some helpful utilities,"
        " making it easier to game with other users in group chats\. It does "
        "this through 2 main features:\n\n"
        f"{values.RIGHT_POINTING_EMOJI} The bot allows you to view the "
        "Online Status of gamers on Xbox Live & PSN through the Status Users "
        "feature\.\n"
        f"{values.RIGHT_POINTING_EMOJI} The bot allows you to create Notify "
        "Groups consisting of other members in a group chat\. You can use a "
        "Notify Group to notify those members when you want to play games "
        "with them, or to send them any other message\.",
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )


def start(update, context):
    """Send a message when the command /start is issued."""
    # 3 pathways from here:
    # someone just ran /start
    # someone ran start to add_status_user, etc.
    # someone ran start to see the help menu
    if update.message.from_user.id == update.message.chat.id:
        db.DBConnection().update_one(
            "chats",
            {"chat_id": update.message.chat.id},
            {"$set": {"chat_id": update.message.chat.id}},
            upsert=True
        )

    if not context.args:
        update.message.reply_animation(
            open(values.OBIWAN_HELLO_THERE_GIF_FILEPATH, "rb")
        )
        msg = update.message.reply_text(
            "You've successfully started me up\! Use /help to learn more "
            "about what I can do for you, or alternatively, just click on "
            f"the button below {values.SMILEY_EMOJI}",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_keyboards.see_help_menu(
                None
                if update.message.from_user.id == update.message.chat.id
                else create_deep_linked_url(
                    context.bot.get_me().username, "help"
                )
            )
        )
        context.user_data[f"help_interface_{msg.message_id}"] = msg
    else:
        arg = context.args[0]
        if arg == "help":
            return help_main_menu(update, context)
        else:
            cmd_code, group_id = arg.split("_")
            group_chat = context.bot.get_chat(group_id)
            group_title = group_chat.title
            update.message.reply_animation(
                open(values.OBIWAN_HELLO_THERE_GIF_FILEPATH, "rb")
            )
            msg = (
                "You've successfully started me up\! Now you can go back to the "
                f"`{group_title}` group chat and run "
            )
            if cmd_code == "asu":
                msg += "`/add_status_user`"
            elif cmd_code == "msu":
                msg += "`/modify_status_user`"
            elif cmd_code == "ang":
                msg += "`/add_notify_group`"
            elif cmd_code == "mng":
                msg += "`/modify_notify_group`"

            update.message.reply_animation(
                open(values.OBIWAN_HELLO_THERE_GIF_FILEPATH, "rb")
            )
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)

    return HELP_MENU


def help_main_menu(update, context):
    """
    Outputs the help main menu with buttons for: general, notify groups, and
    status users
    """
    if update.callback_query:
        update = update.callback_query
        msg_id = update.message.message_id
        update.answer()
        context.user_data[f"help_interface_{msg_id}"].edit_text(
            "Welcome to the help menu\! Choose an option below to learn more "
            "about it",
            reply_markup=inline_keyboards.main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    else:
        if update.message.from_user.id != update.message.chat.id:
            url = create_deep_linked_url(context.bot.get_me().username, "help")
            update.message.reply_text(
                f"[Commands Explanation]({url})",
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
            return ConversationHandler.END

        msg = update.message.reply_text(
            "Welcome to the help menu\! Choose an option below to learn more "
            "about it",
            reply_markup=inline_keyboards.main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        context.user_data[f"help_interface_{msg.message_id}"] = msg
    return HELP_MENU


def help_general(update, context):
    """Lists out the general commands for the help menu"""
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_GENERAL(),
        reply_markup=inline_keyboards.go_back_to_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_memes(update, context):
    """Lists out the memes commands in the help menu"""
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_MEMES(),
        reply_markup=inline_keyboards.go_back_to_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_notify_group_menu(update, context):
    """
    Outputs the help notify gropu main menu with buttons for: add notify group,
    modify notify group, invite to notify group, list notify groups and notify
    """
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_NOTIFY_GROUP(),
        reply_markup=inline_keyboards.notify_group_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_add_notify_group(update, context):
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_ADD_NOTIFY_GROUP(),
        reply_markup=inline_keyboards.go_back_to_notify_group_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_modify_notify_group(update, context):
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_MODIFY_NOTIFY_GROUP(),
        reply_markup=inline_keyboards.go_back_to_notify_group_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_invite_to_notify_group(update, context):
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_INVITE_TO_NOTIFY_GROUP(),
        reply_markup=inline_keyboards.go_back_to_notify_group_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_list_notify_groups(update, context):
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_LIST_NOTIFY_GROUPS(),
        reply_markup=inline_keyboards.go_back_to_notify_group_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_notify(update, context):
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_NOTIFY(),
        reply_markup=inline_keyboards.go_back_to_notify_group_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_status_user_menu(update, context):
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_STATUS_USER(),
        reply_markup=inline_keyboards.status_user_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_add_status_user(update, context):
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_ADD_STATUS_USER(),
        reply_markup=inline_keyboards.go_back_to_status_user_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_modify_status_user(update, context):
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_MODIFY_STATUS_USER(),
        reply_markup=inline_keyboards.go_back_to_status_user_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_status(update, context):
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_STATUS(),
        reply_markup=inline_keyboards.go_back_to_status_user_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_support(update, context):
    """Lists out the support commands in the help menu"""
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_SUPPORT(),
        reply_markup=inline_keyboards.go_back_to_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def help_donate(update, context):
    """Lists out the donate commands in the help menu"""
    update = update.callback_query
    msg_id = update.message.message_id
    update.answer()
    context.user_data[f"help_interface_{msg_id}"].edit_text(
        strings.HELP_DONATE(),
        reply_markup=inline_keyboards.go_back_to_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return HELP_MENU


def f(update, context):
    """Replies with a gif to pay respect."""
    update.message.reply_animation(
        open(values.F_TO_PAY_RESPECT_GIF_FILEPATH, "rb")
    )


def mf(update, context):
    """Replies with a sad.. sad voice note."""
    update.message.reply_audio(
        open(values.MISSION_FAILED_AUDIO_FILEPATH, "rb")
    )


def wdhs(update, context):
    """Replies with the 'What did he say??' TikTok meme"""
    update.message.reply_video(
         open(values.WHAT_DID_HE_SAY_VIDEO_FILEPATH, "rb")
    )


def age(update, context):
    update.message.reply_text(
        "Didn't your mother ever teach you it's not polite to ask a bot its "
        f"age? Anyway, I am {values.AGE} {values.SMILEY_EMOJI}",
        parse_mode=ParseMode.MARKDOWN_V2
    )


def donate(update, context):
    """
    Returns with a bunch of information on how the user can donate to help
    support the bot's maintenance 
    """
    update.message.reply_text(
        strings.DONATION_DETAILS,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=inline_keyboards.donation_options_keyboard()
    )


def donate_using_telegram(update, context):
    """
    Returns an invoice for donating to the bot directly through Telegram
    """
    context.bot.send_invoice(
        update.callback_query.message.chat.id,
        "Supporting Gamers' Utility Bot",
        "The money you donate will be mainly used to pay for server & "
        "maintenance costs",
        "gub_maintenance_costs",
        values.PAYMENT_TOKEN,
        "CAD", 
        [
            LabeledPrice("Minimum Donation", 2 * 100)
        ],
        max_tip_amount=30 * 100,
        suggested_tip_amounts=[1 * 100]
    )


def precheckout_callback(update, context):
    """Answers the PreCheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'gub_maintenance_costs':
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


# finally, after contacting the payment provider...
def successful_payment_callback(update, context):
    """Confirms the successful payment."""
    update.message.reply_text(
        strings.DONATION_THANK_YOU,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def support(update, context):
    """
    Replies with information about a support channel as well as how to
    share feedback
    """
    update.message.reply_text(
        strings.SUPPORT_INFORMATION,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )


def feedback(update, context):
    """Takes the user's feedback and sends them to the list of admins"""
    if not context.args:
        update.message.reply_text(
            "You need to add feedback after the command\. For example:\n\n"
            "`/feedback this bot SUXS!`\n\nAlthough maybe make the feedback "
            f"more constructive than that {values.WINK_EMOJI}",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return
    feedback = " ".join(context.args)
    bot = Bot(values.FEEDBACK_TOKEN)
    for admin_id in values.ADMIN_LIST:
        bot.send_message(admin_id, f"*Feedback*:\n\n{feedback}")


def announce(update, context):
    if update.message.from_user.id not in values.ADMIN_LIST:
        return
    
    if not context.args:
        update.message.reply_text(
            "You need to provide an annoucement message in order to announce, "
            "buddy."
        )
        return
    
    announcement = " ".join(context.args)
    context.user_data["message"] = f"*ANNOUNCEMENT*\n\n{announcement}"
    context.user_data["confirmation_msg"] = update.message.reply_text(
        "Confirm the following announcement?\n\n"
        f"{context.user_data['message']}",
        reply_markup=inline_keyboards.confirm_announcement_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

    return AWAITING_CONFIRMATION 


def confirm_announcement(update, context):
    update = update.callback_query
    update.answer()
    if update.from_user.id not in values.ADMIN_LIST:
        return
    all_chats = db.DBConnection().find("chats", {})
    for chat in all_chats:
        try:
            context.bot.send_message(
                chat["chat_id"],
                context.user_data['message'],
                parse_mode=ParseMode.MARKDOWN
            )
        except Unauthorized:
            # We could remove the chats who have ended up blocking the bot..
            # but I don't really see the use?
            continue
    
    context.user_data["confirmation_msg"].edit_text(
        f"Sent the following announcment to {len(all_chats)} chat(s):\n\n"
        f"{context.user_data['message']}",
        parse_mode=ParseMode.MARKDOWN
    )
    context.user_data.clear()
    return ConversationHandler.END


def cancel_announcement(update, context):
    update = update.callback_query
    update.answer()
    if update.from_user.id not in values.ADMIN_LIST:
        return
    context.user_data["confirmation_msg"].edit_text(
        "Cancelled the announcement."
    )
    context.user_data.clear()
    return ConversationHandler.END


def new_member(update, context):
    for member in update.message.new_chat_members:
        if member.username == context.bot.get_me().username:
            db.DBConnection().update_one(
                "chats",
                {"chat_id": update.message.chat.id},
                {"$set": {"chat_id": update.message.chat.id}},
                upsert=True
            )
            return


def left_member(update, context):
    bot_username = context.bot.get_me().username
    if update.message.left_chat_member["username"] == bot_username:
        db.DBConnection().delete_one("chats", {
            "chat_id": update.message.chat.id
        })


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
