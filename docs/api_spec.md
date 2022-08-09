# Overview

This documentation pertains to the API module that will be created using
FastAPI and GraphQL.

## Why Create an API? 

The purpose of the API module is to be able to organize the code better,
make the project more scalable, and give me an opportunity 
to learn different technologies.

Before, all the API access for the PSN, Xbox, and Steam services was done under
one module. However, I wanted to used FastAPI and GraphQL to give my project
more structure. I also wanted to see whether use of GraphQL in my usecase would
end up giving me any benefit in terms of runtime. 

# Architecture

Architecturally speaking, the api module will be doing the work of getting
player's presences and returning user statuses. This means that all the bot
module will be giving the api module is a list of xbox ids, or psn ids, and
expecting json results that will represent each user's status.

# Design

Another design decision to make is whether I want to 

# Routes

There will be 6 routes for the api module that the bot module will use for
contact.

## GET /xbox/accountid/
This endpoint will take a xbox gamertag, and will return the corresponding
account id for that user

- Receives: xbox_gamertag (type: str | e.g. OoglaBooglaBimboJimbo)
- Returns: { "xbox_account_id": 5729587289758327 }

## GET /xbox/presence/
This endpoint will take a list of xbox account ids, and will return the
corresponding presences for each corresponding user.
- Receives: xbox_account_ids (type: list[int], e.g. [5729587289758327, 4457382856603402])
- Returns:
```
{
    "presences": [
        {
            "account_id": 5729587289758327,
            "platform": "WindowsOneCore",
            "player_state": "AWAY",
            "game_title": "Rocket League | Main Menu"
            "last_seen": "Datetime.datetime()"
        },
        {
            "account_id": 4457382856603402,
            "platform": "Scarlett",
            "player_state": "OFFLINE",
            "game_title": None,
            "last_seen": "2009-07-10 18:44:59.193982+00:00"
        },
    ]
}
```



## GET /psn/accountid/
This endpoint will take a psn online id, and will return the corresponding
account id for that user
## GET /psn/presence/
This endpoint will take a list of psn account ids, and will return the
corresponding presences for each corresponding user.

## GET /steam/accountid/
Not implemented
## GET /steam/presence/
Not implemented