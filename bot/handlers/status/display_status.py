import asyncio
import time

from external_handlers.apis_wrapper import ApisWrapper
from general import values
from telegram import ParseMode



def status(update, context):
    st = time.time()
    message = update.message.reply_text(
        f"{values.RAISED_HAND_EMOJI} Please hold as I fetch the status of the "
        "users in this group\. Note this can take up to 30 seconds\!",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    api_wrapper = ApisWrapper()
    e1 = time.time()
    print('Time to initialize API wrapper:', e1-st, 'seconds')
    players = asyncio.run(
        api_wrapper.get_presence_from_apis(update.message.chat.id)
    )
    e2 = time.time()
    print('Time to get presence from API:', e2-e1, 'seconds')
    if not players:
        message.edit_text("You have no status users set to display the status "
                          "of\. Use /add_status_user to add a status user")
        return
    players = [str(player) for player in players]
    e3 = time.time()
    print('Time to stringize status:', e3-e2, 'seconds')
    message.edit_text("".join(players))
    e4 = time.time()
    print('Time to message status:', e4-e3, 'seconds')
