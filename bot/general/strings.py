from general import values


# Below are the list of strings related to the Bot's UI

HELP_GENERAL = lambda : (
    "*General Commands*\n"
    "/start — Starts the bot up\.\n"
    "/about — Tells you a bit about the bot\.\n"
    "/age — The bot will reply with how old the bot is\.\n\n"

    "*Support*\n"
    "/help — The bot will send a menu containing help on all the commands "
    "available to the user\.\n"
    "/support — The bot will give you details about how to recieve support "
    "for the bot\n"
    "/feedback — Used to submit feedback regarding the bot\n\n"

    "*Memes*\n"
    "/f — The \"Press F to Pay Respect\" GIF\.\n"
    "/mf — The \"Mission failed, we'll get 'em next time\" audio clip\n"
    "/wdhs — The \"What did he say??\" TikTok video clip\n"
)

HELP_NOTIFY_GROUP = lambda : (
    "Your Notify Groups are used to notify a group of people that you choose "
    "\(with an optional message\) without having to constantly retype their "
    "username tags\.\n\n"
    "Choose an option below to learn more about a notify group command"
)

HELP_ADD_NOTIFY_GROUP = lambda : (
    "*Usage:* `/add_notify_group`\n\n"
    "\- You can use this command only in a group\n"
    "\- After entry, the bot will contact you in private chat\n"
    "\- The bot will ask you questions about the Notify Group that you want "
    "to create\n"
    "\- This Notify Group that you create will reside in the group chat you "
    "originally entered the command in\n"
)

HELP_MODIFY_NOTIFY_GROUP = lambda : (
    "*Usage:* `/modify_notify_group`\n\n"
    "\- You can use this command only in a group\n"
    "\- After entry, the bot will contact you in private chat\n"
    "\- If you are admin of the group chat where you entered the command in, "
    "you will be able to delete all the Notify Groups in the group chat\. "
    "However, you will only be able to edit the Notify Groups that you "
    "created\. You will NOT be able to edit the Notify Groups of others\n"
    "\- If you are not an admin of the group chat where you entered the "
    "command in, you will be able to edit/delete the Notify Groups that you "
    "created"
)

HELP_INVITE_TO_NOTIFY_GROUP = lambda : (
    "*Usage:* `/invite_to_notify_group name_of_notify_group @person_to_invite1"
    " @person_to_invite2 ...`\n\n"
    "\- You can use this command only in a group\n"
    "\- After entry, you are able to revoke the invite you sent out\n"
    "\- You will not be able to use this command for a Notify Group that you "
    "did not create\n"
)

HELP_LIST_NOTIFY_GROUPS = lambda : (
    "*Usage:* `/list_notify_groups`\n\tOR `/list_notify_groups "
    "name_of_notify_group_1 name_of_notify_group_2 ...`\n\n"
    "\- You can use this command only in a group\n"
    "\- You can choose to provide arguments after the command or not\n"
    "\- If you don't provide arguments, all notify groups in the group chat "
    "will be listed\n"
    "\- If you provide arguments, only the notify groups specified after the "
    "the command will be listed\n"
)

HELP_NOTIFY = lambda : (
    "*Usage:* `/notify name_of_notify_group`\n\tOR "
    "`/notify name_of_notify_group the message to send`\n\n"
    "\- You can use this command only in a group\n"
    "\- You need to provide the name of the notify group after the command\n"
    "\- You can choose to include an optional message which will be added to "
    "the notification message\n"
    "\- The creator of the Notify Group AND all members in a Notify Group are "
    "able to use the notify command for their Notify Group\n"
)

HELP_STATUS_USER = lambda : (
    "Your Status Users are a user that you create that can be used to show "
    "your online status, what game you're playing, or when you were last "
    "online\. You can connect your Xbox Gamertag and/or your PSN Online ID to "
    "a Status User\. Status Users strictly exist in whatever chat you created "
    "them, whether that is a group chat or a private chat\.\n\n"
    "Choose an option below to learn more about the Status User commands"
)

HELP_ADD_STATUS_USER = lambda : (
    "*Usage:* `/add_status_user`\n\n"
    "\- You can use this command in both private chat and group chats\n"
    "\- The Status User you create will reside in the group chat you "
    "originally entered the command in, or in the private chat with the bot "
    "if that's where you entered the command\n"
    "\- After entry, the bot will contact you in private chat\n"
    "\- The bot will ask you questions about the Status User you want to "
    "create\n"
)

HELP_MODIFY_STATUS_USER = lambda : (
    "*Usage:* `/modify_status_user`\n\n"
    "\- You can use this command in both private chat and group chats\n"
    "\- After entry, the bot will contact you in private chat\n"
    "\- If you are admin of the group chat where you entered the command in, "
    "you will be able to delete all the Status Users in the group chat\. "
    "However, you will only be able to edit the Status Users that you "
    "created\. You will NOT be able to edit the Status Users of others\n"
    "\- If you are not an admin of the group chat where you entered the "
    "command in, you will be able to edit/delete the Status Users that you "
    "created"
)

HELP_STATUS = lambda : (
    "*Usage:* `/status`\n\n"
    "\- You can use this command in both private chat and group chats\n"
    "\- This command will list all the Status Users connected to the chat "
    "that the command was executed in\n"
    "\- A Status User's Xbox Gamertag or PSN Online ID are always hidden\.\n"
)

## DONATION STRINGS

DONATION_DETAILS = (
    "Pleased to hear you're thinking about donating\! Every month, the server "
    "costs of running this bot totals to around $30 every month\. That cost "
    "is mainly paid by my creator\. If you would like to support the "
    "maintenance of this bot, you can donate using one of the 3 ways below\n\n"
    "*GitHub*: 100\% of the proceeds go directly to my creator\. You can do a "
    "one\-time donation, or pay $1, $3, or $5 every month \(your choice\)\n\n"
    "*Telegram*: Roughly 3\% of your donation is taken by the payment provider"
    " \(Stripe\)\n\n"
    "*PayPal*: Roughly 3\% of your donation is taken by the payment provider "
    "\(PayPal\)\n\n"
    "All options are provided in the buttons below\. Thank you "
    f"{values.SMILEY_EMOJI}"
)

DONATION_THANK_YOU = (
    f"Thank you so much for donating {values.SMILEY_EMOJI} I hope you "
    "continue to enjoy using my services"
)

## SUPPORT STRING

SUPPORT_INFORMATION = (
    "If you're looking to share feedback or have found something wrong with "
    "the bot, you can do either of the two things below:\n\n"
    "1\. You can let the developers know by creating an 'issue' over at this "
    "[link](https://github.com/AhmedNSidd/gamers-social-manager-telegram-bot/"
    "issues)\n\n"
    "2\. You can simply run `/feedback replace_this_with_your_feedback`"
    "\n\nIf you're just looking for a support channel where you'll receive "
    "announcements on the bot, you can join @GamersUtilityBotSupport"
)

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
    f"4\) Run {cmd} again"
)


## UI text for the common.py handlers
cancel_command_due_to_new_command = (
    "The {} command has been cancelled due to the entry of a new command"
)