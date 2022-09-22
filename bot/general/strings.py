# Below are the list of strings related to the Bot's UI

# *********************************************************************
# STATUS USER STRINGS
# *********************************************************************

## ADD STATUS USER STRINGS

CLICK_BUTTON_TO_START_PROCESS = lambda process: (
    f"Click on the button below to start the process of {process}"
)

ASU_INTRO = lambda user_mention, group_name: (
    f"Hey {user_mention}\!\n\nWe will add a status user to " + (
        f"the _{group_name}_ group" if group_name else "this private chat"
    ) + "\. I will ask you for your display name/Xbox Live/PSN/Steam IDs\. "
    "You can choose to add these to your status user, or choose to skip if "
    "would prefer to not connect these services to your status user\.\n\nYou "
    "can also choose to cancel the process of adding this status user at any "
    "point during this process"
)


ASU_ENTER_DISPLAY_NAME = lambda group_name: (
    "Enter the *display name* for the status user you want to add to "
    f"{group_name}\n\nYou can not skip this entry"
)

ASU_INVALID_DISPLAY_NAME = lambda : (
    "You did not provide a valid display name\. Please enter a unique display "
    "name"
)

ASU_DUPLICATE_DISPLAY_NAME = lambda group_name: (
    "Somebody with that display name already exists in " + (
        f"the _{group_name}_ group" if group_name else "this private chat"
    ) + "'s status\. Please enter a unique display name",
)

ASU_DISPLAY_NAME_SUCCESS = lambda display_name: (
    f"Great\! Your display name has been set as `{display_name}`"
)

ASU_XBOX_GAMERTAG_PROMPT = lambda: (
    "Now enter your *Xbox Gamertag*"
)

ASU_INVALID_XBOX_GAMERTAG_ERROR = lambda: (
    "You did not provide a valid Xbox Gamertag\. Please enter a valid Xbox "
    "Gamertag"
)


# *********************************************************************
# COMMON
# *********************************************************************

BOT_SENT_A_PRIVATE_MESSAGE = lambda mention, objective: (
    f"Hey {mention}\!\n\nI have sent you a private message which you can "
    f"use {objective}"
)

BOT_UNABLE_TO_SEND_PRIVATE_MESSAGE = lambda mention, cmd_name, cmd: (
    f"Hey {mention}\!\n\nThe bot was unable to send you a private message "
    f"regarding {cmd_name} because you have to start the bot privately "
    "first\. Please follow these instructions:\n\n"
    "1\) Click the button below to go to your private chat\n"
    "2\) Click on the **start** button to start the bot\n"
    "3\) Come back to this group chat\n"
    f"4\) Run `{cmd}` again"
)


## UI text for the common.py handlers
cancel_command_due_to_new_command = (
    "The {} command has been cancelled due to the entry of a new command"
)