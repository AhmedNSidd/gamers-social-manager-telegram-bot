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

This section outlines the steps required to get this project up and running on your local dev environment.

## Prerequisites

1. [Install Docker](https://docs.docker.com/get-docker/)
2. [Install Docker Compose](https://docs.docker.com/compose/install/)

## Environment Variables

For your local development environment setup, you will require a `.env` file. Create this file in the root directory of the project.
Copy the contents of the `.env.example` file into this file, and populate the value for the `GUB_TESTING_BOT_TOKEN` key.

### Generating a GUB_TESTING_BOT_TOKEN

We will need an API token to access the [BotsAPI from telegram](https://core.telegram.org/bots/api). In order to generate one:

1. Open Telegram Messenger either via their [app](https://telegram.org/) (available on many different platforms) or through [web](https://web.telegram.org/k/) (Note you will need to sign up and create an account if you don't have one already)
2. In the search bar, type in `@BotFather` and select the verified profile of `@BotFather`
3. Start the bot and issue the command `/newbot` in the chat to create a new testing bot and follow the steps outlined by `@BotFather`
4. Once you have finished creating your testing bot, `@BotFather` will provide you with the link that you can use to access your newly created bot, which will eventually run the GUB bot, and `@BotFather` will also provide the token which you can insert into the .env file
5. Copy the Bot API token from the response message and paste it into the `.env` file

## Spinning up your bot

Once you have generated the API token and have setup your `.env` file, run the following command from the root directory of the project:
```
docker-compose up --build
```
This will install all required dependencies, build all images, start up the containers and get the app up and running.

Note: Once you have gotten the app built and running, it is not necessary to pass the `--build` option to the `docker-compose up` command to rebuild the project on subsequent runs. You can find more information about how `docker-compose` works [here](https://docs.docker.com/engine/reference/commandline/compose_up/).

Use the link that `@BotFather` provides in order to access the bot. You can verify that it is running by visiting telegram, and you should be able to interact with it by issuing commands such as `/start` or `/about`.

# Contributions / Open Source

