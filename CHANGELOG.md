# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Add option to display help main menu when running start
- Add a command for the "What Did He Say???" TikTok Meme
- Add a command to allow user to donate to support the bot's creator
### Changed
- Always show help instructions in private chat.
### Removed


## [v1.0.0]
### Added
- Add further instructions for user when they start the bot after they were
unable to run a command before because the bot was blocked/not started
- Add the ability to list specific notify groups if they are provided as
command arguments to the /list_notify_groups command.
- List notify groups alphabetically when notify groups are listed using the
/list_notify_groups command.
- Add a button to the add/modify notify group process to use the alternative
name for the notify group.
- Adds autocomplete for commands, an about & description for the bot, as well
as connects payments methods to the bot.
### Changed
- Fixes the v0.1.0 link for CHANGELOG.md
- Instead of setting the notify group names as pre-formatted, the bot will bold
them when a notify group is to be stringized.
- Turned the help message into a help menu
- Allows Notify Group command arguments to be case-insensitive.
- Fix a typo in the /about command text
### Removed


## [v0.1.0]

### Added
- Created a CHANGELOG.md
- Add a Semantic Version to keep track of bot version
- The bot will now remove /notify command messages from the group chat if the
bot has permissions to delete messages
- More user feedback and engagement from the bot in the invitation to notify
group flow
- Created an /about command that gives the user information about the bot,
its version, its creator, and what it offers the user

### Changed
- Change command ordering of Dockerfile to promote faster
building
- Modify requirements.txt to only keep essential 
requirements
- Fix some typos in messages from the bot
- Improve on the formatting of the /status command output by increasing
whitespace appropriately and changing "XBOXLIVE" -> "Xbox Live"
- Fixed bug where status user's display name was set as None after
creation of a status user
- Fixed a bug where user mentions' texts were set as None on
creation and modification of a status user
- Fixed bad command usage that was serving as a help for the user for
the /modify_notify_group command in the invite to notify group flow
- Improve user prompt when there are no status users to disply the status of
- Allow multiple invites to a notify group



[Unreleased]: https://github.com/AhmedNSidd/gamers-social-manager-telegram-bot/compare/main...develop
[v1.0.0]: https://github.com/AhmedNSidd/gamers-social-manager-telegram-bot/releases/tag/v1.0.0
[v0.1.0]: https://github.com/AhmedNSidd/gamers-social-manager-telegram-bot/releases/tag/v0.1.0
