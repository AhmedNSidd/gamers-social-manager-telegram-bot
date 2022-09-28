from general.values import RIGHT_POINTING_EMOJI, CANCELLED_EMOJI, NEXT_TRACK_EMOJI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.utils.helpers import create_deep_linked_url


def cancel_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            f"{CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
    ]])

def asu_xbox_gamertag_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            f"{CANCELLED_EMOJI} CANCEL",
            callback_data=f"cancel"
        ),
        InlineKeyboardButton(
            f"{NEXT_TRACK_EMOJI} SKIP THIS ENTRY",
            callback_data=f"skip_xbox_gamertag"
        )
    ]])

def go_to_private_chat_keyboard(username, payload=None):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            f"{RIGHT_POINTING_EMOJI} GO TO PRIVATE CHAT",
            url=(f"https://t.me/{username}" if not payload else
                 create_deep_linked_url(username, payload))
        )]]
    )

def asu_start_keyboard(chat_id):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "ADD STATUS USER",
                callback_data=f"asu_{chat_id}"
            )
        ]]
    )

def msu_start_keyboard(chat_id):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "MODIFY STATUS USERS",
                callback_data=f"msu_{chat_id}"
            )
        ]]
    )

def ang_start_keyboard(chat_id):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "ADD NOTIFY GROUP",
                callback_data=f"ang_{chat_id}"
            )
        ]]
    )

def mng_start_keyboard(chat_id):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "MODIFY NOTIFY GROUP",
                callback_data=f"mng_{chat_id}"
            )
        ]]
    )