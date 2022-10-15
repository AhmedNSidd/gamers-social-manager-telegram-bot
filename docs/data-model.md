# Overview
For our database, we will use mongodb as it is a technology that I was
interested in learning.

# Collections Schema
We will have 4 collections: users, credentials, statususers, notifygroups

## chats

Each document in the chats collection signifies either a telegram user or a
telegram chat that has used GUB. So when the bot is added to a group, it stores
the chat id of that group. It also promptly deletes that group's chat id if
the bot is removed.
```
{
    '_id': <bson object id>,
    'chat_id': <int>
}
```


## credentials

There will be 3 documents in this collection for Xbox, PSN, and Steam, each
having one credential document.
```
Xbox credential schema:
{
    "_id": <bson object id>,
    "platform": "xbox",
    "client_id": <str>,
    "client_secret": <str>,
    "tokens": {
        "token_type": <str>,
        "expires_in": <int>,
        "scope": <str>,
        "access_token": <str>,
        "refresh_token": <str>,
        "user_id": <str>,
        "issued": <datetime>,
    }
}

PSN credential schema:
{
    "_id": <bson object id>,
    "platform": "psn",
    "npsso": <str>
}

Steam credential schema:

```

## statususers

Each document in the statusers collection will contain the following schema 
corresponding to one status user.
```
{
    '_id': <bson object id>,
    'user_id': <int>,
    'chat_id': <int>,
    'group_name': <str|None>,
    'display_name': <str>,
    'xbox_account_id': <str>,
    'xbox_gamertag': <str>,
    'psn_account_id': <str>,
    'psn_online_id': <str>
}
```

## notifygroups

Each document in the notifygroups collection will contain the following schema 
corresponding to one notify group.
```
{
    '_id': <bson object id>,
    'chat_id': <int>,
    'creator_id': <int>,
    'name': <str>,
    'description': <str|None>,
    'members': <int[]>,
    'invited': <int/str[]> # can be usernames 
}
```

## notifygroupinvitation

Each document in the notifygroupinvitation collection will contain the
following schema corresponding to one invitation to a notify group.
```
{
    '_id': <bson object id>,
    'notify_group_id': <bson object id>,
    'initially_invited': <int/str[]> # all users who were initially invited
    'actively_invited': <int/str[]> # the users who have still yet to accept/reject an invite
}
```
