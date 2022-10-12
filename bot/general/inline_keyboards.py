from general import values
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.utils.helpers import create_deep_linked_url

# *********************************************************************
# GENERAL KEYBOARDS
# *********************************************************************

#### START KEYBOARDS

def see_help_menu(url=None):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{values.LEDGER_EMOJI} SEE HELP MENU",
                callback_data=f"help_main_menu"
            )
            if not url else
            InlineKeyboardButton(
                f"{values.LEDGER_EMOJI} SEE HELP MENU",
                url=url
            )
        ],
    ])

#### HELP KEYBOARDS

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{values.INFORMATION_DESK_PERSON_EMOJI} GENERAL",
                callback_data=f"general"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{values.CONTROLLER_EMOJI} STATUS USERS",
                callback_data=f"status_user_menu"
            ),
            InlineKeyboardButton(
                f"{values.BELL_EMOJI} NOTIFY GROUPS",
                callback_data=f"notify_group_menu"
            ),
        ]
    ])

def go_back_to_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK",
                callback_data=f"help_main_menu"
            ),
        ],
    ])

def notify_group_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{values.PLUS_EMOJI} ADD NOTIFY GROUP",
                callback_data=f"add_notify_group"
            ),
            InlineKeyboardButton(
                f"{values.PENCIL_EMOJI} MODIFY NOTIFY GROUP",
                callback_data=f"modify_notify_group"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{values.ENVELOPE_EMOJI} INVITE TO NOTIFY GROUP",
                callback_data=f"invite_to_notify_group"
            ),
            InlineKeyboardButton(
                f"{values.NOTEPAD_EMOJI} LIST NOTIFY GROUPS",
                callback_data=f"list_notify_groups"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{values.BELL_EMOJI} NOTIFY",
                callback_data=f"notify"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK",
                callback_data=f"help_main_menu"
            ),
        ],
    ])

def go_back_to_notify_group_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK",
                callback_data=f"notify_group_menu"
            ),
        ],
    ])


def status_user_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{values.PLUS_EMOJI} ADD STATUS USER",
                callback_data=f"add_status_user"
            ),
            InlineKeyboardButton(
                f"{values.PENCIL_EMOJI} MODIFY STATUS USER",
                callback_data=f"modify_status_user"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{values.ONLINE_EMOJI} DISPLAY STATUS",
                callback_data=f"status"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK",
                callback_data=f"help_main_menu"
            ),
        ],
    ])


def go_back_to_status_user_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{values.LEFT_POINTING_EMOJI} GO BACK",
                callback_data=f"status_user_menu"
            ),
        ],
    ])

#### DONATION KEYBOARDS

def donation_options_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"GitHub",
                url=f"https://github.com/sponsors/AhmedNSidd/dashboard"
            ),
        ],
        [
            InlineKeyboardButton(
                f"Telegram",
                callback_data=f"donate_using_telegram"
            ),
        ],
        [
            InlineKeyboardButton(
                f"PayPal",
                url="https://paypal.me/GamersUtilityBot?country.x=CA&locale.x=en_US"
            ),
        ],
    ])

# *********************************************************************
# COMMON KEYBOARDS
# *********************************************************************


def cancel_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
    ]])

def asu_xbox_gamertag_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            f"{values.CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{values.NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_xbox_gamertag"
        )
    ]])

def go_to_private_chat_keyboard(username, payload=None):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            f"{values.RIGHT_POINTING_EMOJI} GO TO PRIVATE CHAT",
            url=(f"https://t.me/{username}" if not payload else
                 create_deep_linked_url(username, payload))
        )]]
    )

def asu_start_keyboard(chat_id):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                f"{values.PLUS_EMOJI} ADD STATUS USER",
                callback_data=f"asu_{chat_id}"
            )
        ]]
    )

def msu_start_keyboard(chat_id):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                f"{values.PENCIL_EMOJI} MODIFY STATUS USERS",
                callback_data=f"msu_{chat_id}"
            )
        ]]
    )

def ang_start_keyboard(chat_id):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                f"{values.PLUS_EMOJI} ADD NOTIFY GROUP",
                callback_data=f"ang_{chat_id}"
            )
        ]]
    )

def mng_start_keyboard(chat_id):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                f"{values.PENCIL_EMOJI} MODIFY NOTIFY GROUP",
                callback_data=f"mng_{chat_id}"
            )
        ]]
    )