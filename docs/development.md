# Introduction 

This is a documentation of important development information for the
developers. 

# Project Layout

- `./external_handlers` contains code responsible for interacting with the 
Playstation and Xbox APIs. More information about these APIs can be found in
the [APIs Used section](#apis-used)

- `./general` contains static values and settings, as well as general helper
functions.

- `./handlers` contains the logic for the responses to the commands recieved by
the bot in `./bot.py`. Namely the basic commands (such as quips, help, etc.)
as well as the notifying and status commands.

- `./models` contains User models that are used in conjunction with the 
`./external_handlers` module. The models help parse the responses given by the
APIs.

- `./test` contains code that tests the APIs used by the `./external_handlers`
module. 

# Database Setup

A postgresql database is created in the Heroku app. You can connect to it
through `heroku pg:psql --app chaddicts-tg-bot`, but only through Ahmed's
Heroku credentials.


# APIs Used {#apis-used}

- The new Xbox API that is used can be found
[here](https://github.com/OpenXbox/xbox-webapi-python). The old Xbox API we
used to use can be found [here](https://xapi.us/).We stopped using it because
there was a limit on how many times the API could be called. 

- The new PSN API that is used can be found
[here](https://github.com/OpenXbox/xbox-webapi-python)
