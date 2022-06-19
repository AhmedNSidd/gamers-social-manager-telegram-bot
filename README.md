# Gamers' Social Manager Telegram Bot
This is a bot made for the Telegram Messenger application. The purpose of this
bot is to connect gamers. It does this through two features:

- The ability for a user to see the online statuses of the players they choose
on a gaming platform that they wish (Xbox, Playstation, or Steam)
- The ability to notify all players in a group when it's time to play games.

This is the ideal bot to add to your Telegram group if your group contains
gamers that play on Xbox, Playstation, or Steam, and you all regularly play
with each other.

The bot can be found at https://t.me/GamersSocialManagerBot

# Overview of All Available Commands

## General Commands
```
/help -- The bot will send this message that you're reading right now.

/f -- The bot will reply with a gif to help pay respect.

/mf -- The bot will reply with a sad... sad.. voice note.

/age -- The bot will reply with how old the bot is.
```
## Notify Commands 
### Send a preset message while tagging preset users
```
/add_notify_user [username without @] -- The bot will add the username to the list of people you want to notify

/remove_notify_user [username without @] -- The bot will delete the username from the list of people you want to notify

/set_notify_msg [message] -- The bot will set this as the message that will be sent when you run /notify

/notify_info -- The bot will display the list of users who've been set to be notified, as well as the notify message, without actually tagging users.

/notify -- The bot will send the preset message while tagging the preset users.
```


## Status Commands
### Get status of players on Xbox Live, PSN, and Steam
```
/add_status -- The bot will ask you for the online IDs for the corresponding service you wish to display the online status for (Xbox Live, PSN, Steam).

/remove_status [display_name] -- The bot will stop displaying the statuses for the user that is associated with the display name.

/status -- The bot will list the online statuses of the added users, as well as the game that they are currently playing, or the last time they were seen online 
```
# Features Overview

In this section, we will go into more details on the main features of this bot:
Notify and Status

## Notify


- /add_notify_user [username without @]

This command is used to setup the main command (/notify) by adding in the a user 

- /remove_notify_user [username without @]

- /set_notify_msg [message]

- /notify_info

- /notify



## Status


# Running The Bot

## Environment Variables

# Contributions / Open Source

