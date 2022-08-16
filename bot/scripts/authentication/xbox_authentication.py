"""
Script for storing Xbox authentication credentials into the database in the
DATABASE_URL. This script assumes that a table with the proper schema already
exists at the database. If this is not the case, look into running
scripts/db/instantiate_tables.py first.

For more information on the obtaining of these Xbox authentication credentials,
reference the DEVELOPMENT.md file at the root of project.
"""
import argparse
import asyncio
import json
import pathlib
import sys
import webbrowser

sys.path.append(pathlib.PurePath(pathlib.Path(__file__).parent.absolute(),
                                 "../..").__str__())

from aiohttp import ClientSession, web
from general.db import DBConnection
from utils import import_root_dotenv_file
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from xbox.webapi.scripts import REDIRECT_URI


queue = asyncio.Queue(1)

async def auth_callback(request):
    error = request.query.get("error")
    if error:
        description = request.query.get("error_description")
        print(f"Error in auth_callback: {description}")
        return
    # Run in task to not make unsuccessful parsing the HTTP response fail
    asyncio.create_task(queue.put(request.query["code"]))
    return web.Response(
        headers={"content-type": "text/html"},
        text="You can close this tab now.",
    )

async def async_main(client_id: str, client_secret: str, redirect_uri: str):
    async with ClientSession() as session:
        auth_mgr = AuthenticationManager(
            session, client_id, client_secret, redirect_uri
        )
        # Here we need to access the database, 
        # if there are existing tokens AND the secrets match, then we can just
        # refresh the tokens otherwise, we need to create new tokens.
        credentials = DBConnection().find_one("credentials",
                                              {"platform": "xbox"})

        if not credentials or credentials["client_secret"] != client_secret:
            auth_url = auth_mgr.generate_authorization_url()
            webbrowser.open(auth_url)
            code = await queue.get()
            await auth_mgr.request_tokens(code)
            tokens = json.loads(auth_mgr.oauth.json())
            # tokens["issued"] = str(tokens["issued"])
            if not credentials:
                DBConnection().insert_one("credentials",
                    {
                        "platform": "xbox",
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "tokens": tokens
                    }
                )
            else:
                DBConnection().update_one(
                    "credentials",
                    {"platform": "xbox"},
                    {"$set": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "tokens": tokens
                    }}
                )
        else:
            auth_mgr.oauth = OAuth2TokenResponse.parse_raw(
                json.dumps(credentials["tokens"])
            )
            try:
                await auth_mgr.refresh_tokens()
            except:
                print("Error refreshing tokens")
                exit(-1)

            tokens = json.loads(auth_mgr.oauth.json())
            DBConnection().update_one(
                "credentials",
                {"platform": "xbox"},
                {"$set": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "tokens": tokens
                }}
            )
                
        print("Success! The Xbox API is now ready to be used.")

def main():
    parser = argparse.ArgumentParser(description="Authenticate with XBL")
    parser.add_argument(
        "--client-id",
        "-cid",
        help="OAuth2 Client ID",
        required=True
    )
    parser.add_argument(
        "--client-secret",
        "-cs",
        help="OAuth2 Client Secret",
        required=True
    )

    args = parser.parse_args()
    # Import the database's credentials from our root .env file
    import_root_dotenv_file()

    app = web.Application()
    app.add_routes([web.get("/auth/callback", auth_callback)])
    runner = web.AppRunner(app)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, "localhost", 8080)
    loop.run_until_complete(site.start())
    loop.run_until_complete(
        async_main(args.client_id, args.client_secret, REDIRECT_URI)
    )


if __name__ == "__main__":
    main()