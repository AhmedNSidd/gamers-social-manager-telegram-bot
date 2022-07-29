# Overview

This bot needs a command that is able to notify a group of members when it is
time to play video games. We ideally want separate groups so different groups
that want to play with each other can only notify each other without disturbing
others.

# Use Cases

- Our use case is that we are a group of gamers. Some of us want to play
Warzone every evening, while others play other games on the weekends.

- Some other use cases may include a public group where not everyone knows each
other. They basically want to stay private and not be disturbed, but just game
and chill with people they already know. Others are probably looking for some
other people to game with.

- In any case, I'm sure it'd be preferable for anybody in the notify group
to be able to notify others. If this is being abused, the creator of the group
can kick anyone who's being annoying.

- If someone is a total stranger, it'd be cool for them to be able to join
notify groups that are open. 


# Features

## Main Features

- People need to be able to create a notify group to begin with.
- People need to be able to invite others to their notify group (only creators
should be able to do this).
- People need to be able to list all notify groups within a group chat.
- People need to be able to join open notify groups.
- People need to be able to manage their notify groups so they can kick, edit,
or delete
- People need to be able to notify others.

## Other Ideas

- Maybe add status users to notify groups?
- Maybe there should be a feature for a notify group not to show up when people
list notify groups. 

# Development Details

## Modify Notify Group

This command will be mainly used to manage the notify groups that users have
created or are a part of. We will need to change some stuff in the backend
to make this command happen. Specifically, we need to setup user table that
contains a user's id, with their username, their status users, and their notify
groups. Before we make this change however, it may be prudent to change to a
MongoDB, and before we do that, it may be prudent to change this project to
use Scrum development.
