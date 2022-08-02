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
import pathlib
import sys
import webbrowser

sys.path.append(pathlib.PurePath(pathlib.Path(__file__).parent.absolute(),
                                 "../..").__str__())

from aiohttp import ClientSession, web
from general.db import DBConnection, SELECT_WHERE, UPDATE_WHERE, INSERT
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
        existing_credentials = DBConnection().fetchone(
            SELECT_WHERE.format("xboxClientID, xboxClientSecret, xboxTokenType,"
                " xboxExpiresIn, xboxScope, xboxAccessToken, xboxRefreshToken,"
                " xboxUserID, xboxIssued", "Credentials", "id = 1"))

        if existing_credentials and existing_credentials[1] == client_secret:
            tokens = {
                "token_type": existing_credentials[2],
                "expires_in": existing_credentials[3],
                "scope": existing_credentials[4],
                "access_token": existing_credentials[5],
                "refresh_token": existing_credentials[6], 
                "user_id": existing_credentials[7], 
                "issued": existing_credentials[8]
            }
            auth_mgr.oauth = OAuth2TokenResponse.parse_raw(tokens)
            try:
                await auth_mgr.refresh_tokens()
            except:
                print("Error refreshing tokens")

            tokens = auth_mgr.oauth.dict()
            DBConnection().execute(UPDATE_WHERE.format(
                "Credentials", f"xboxTokenType = '{tokens['token_type']}',"
                f" xboxExpiresIn = {tokens['expires_in']},"
                f" xboxScope = '{tokens['scope']}',"
                f" xboxAccessToken = '{tokens['access_token']}',"
                f" xboxRefreshToken = '{tokens['refresh_token']}',"
                f" xboxUserID = '{tokens['user_id']}',"
                f" xboxIssued = '{tokens['issued']}'", "id = 1"))
        else:
            # here we need to create new token
            auth_url = auth_mgr.generate_authorization_url()
            webbrowser.open(auth_url)
            code = await queue.get()
            await auth_mgr.request_tokens(code)
            tokens = auth_mgr.oauth.dict()
            if existing_credentials:
                DBConnection().execute(UPDATE_WHERE.format(
                    "Credentials", f"xboxClientID = '{client_id}',"
                    f" xboxClientSecret = '{client_secret}',"
                    f" xboxTokenType = '{tokens['token_type']}',"
                    f" xboxExpiresIn = {tokens['expires_in']},"
                    f" xboxScope = '{tokens['scope']}',"
                    f" xboxAccessToken = '{tokens['access_token']}',"
                    f" xboxRefreshToken = '{tokens['refresh_token']}',"
                    f" xboxUserID = '{tokens['user_id']}',"
                    f" xboxIssued = '{tokens['issued']}'", "id = 1"))
            else:
                DBConnection().execute(INSERT.format(
                    "Credentials (id, xboxClientID, xboxClientSecret,"
                    " xboxTokenType, xboxExpiresIn, xboxScope,"
                    " xboxAccessToken, xboxRefreshToken, xboxUserID,"
                    " xboxIssued)", f"VALUES(1, '{client_id}', "
                    f"'{client_secret}', '{tokens['token_type']}', "
                    f"{tokens['expires_in']}, '{tokens['scope']}', "
                    f"'{tokens['access_token']}', '{tokens['refresh_token']}',"
                    f" '{tokens['user_id']}', '{tokens['issued']}')"))
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