import asyncio
import os
import psycopg2
from aiohttp import ClientSession, web
from general.values import ADMIN_LIST, BOT_LINK
from telegram import ParseMode
from telegram.ext import ConversationHandler
import urllib.parse as urlparse

from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from general.values import XBOX_AUTH_REDIRECT_URI


# Conversation states for the CommandHandler for Xbox Credentials
TYPING_CLIENT_ID, TYPING_CLIENT_SECRET = range(2)
# Conversation states for the CommandHandler for PSN Credentials
TYPING_NPSSO = 0

url = urlparse.urlparse(os.environ['DATABASE_URL'])

def xbox_credentials_setup(update, context):
    """Asks the user privately for the Xbox Client ID"""
    if update['message'].from_user.id in ADMIN_LIST:
        try:
            update['message'].from_user.send_message(text="Enter the Xbox Client ID.")
            return TYPING_CLIENT_ID
        except:
            update.message.reply_text(text=f"You need to start the bot privately first! Click <a href='{BOT_LINK}'>here</a> and click on start/restart. Then try this command again.", parse_mode=ParseMode.HTML)
            return ConversationHandler.END

def store_xbox_client_id(update, context):
    """Stores the user provided Xbox Client ID and asks the user for the
    Xbox Client Secret"""
    context.user_data["xbox_client_id"] = update.message.text
    update.message.reply_text(f"Client ID has been stored as {update.message.text}. Now please enter the Xbox Client Secret.")
    return TYPING_CLIENT_SECRET


def store_xbox_client_secret(update, context):
    """Stores the user provided Xbox Client ID and asks the user for the
    Xbox Client Secret"""
    client_id = context.user_data["xbox_client_id"]
    client_secret = update.message.text
    context.user_data.clear()
    # Now get the preexisting client secret and client id (if they even exist)
    # if they don't exist, or are different from the user provided ones, then
    # update the existing record or create a new one accordingly. However, if
    # the credentials are the same, then just simply refresh the tokens.
    existing_credentials = None
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM xbox_credential")
            existing_credentials = cursor.fetchone()

    app = web.Application()
    print("1")

    if (not existing_credentials or 
        existing_credentials[1] != client_id or
        existing_credentials[2] != client_secret):
        app = web.Application()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        queue = asyncio.Queue(1)

        print("12")
        # Function definiton for the callback endpoint hit after auth
        # is completed.
        print("14")
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
                text="<script>window.close()</script>",
        )

        app.add_routes([web.get("/auth/callback", auth_callback)])
        runner = web.AppRunner(app)
        print("15")
        print("13")
        
        loop.run_until_complete(runner.setup())
        print("16")
       
        site = web.TCPSite(runner, "localhost", 8080)
        print("17")
        loop.run_until_complete(site.start())
        print("18")

        async def async_main(
            client_id: str, client_secret: str, redirect_uri: str, update
        ):
            async with ClientSession() as session:
                print("22")
                auth_mgr = AuthenticationManager(
                    session, client_id, client_secret, redirect_uri
                )
                print("23")
                # Request new ones if they are not valid
                auth_url = auth_mgr.generate_authorization_url()
                print("24")
                update.message.reply_text(f"Client Secret has been stored as {update.message.text}. Finally, login with your Microsoft Account so your token can be stored by clicking <a href='{auth_url}'>here</a>.", parse_mode=ParseMode.HTML)
                print("25")
                code = await queue.get()
                print("26")
                await auth_mgr.request_tokens(code)
                print("27")
                tokens = auth_mgr.oauth.dict()
                print("28")
                return tokens


        tokens = loop.run_until_complete(
            async_main(client_id, client_secret, XBOX_AUTH_REDIRECT_URI, update)
        )
        print("19")
        with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
            with conn.cursor() as cursor:
                if existing_credentials:
                    # Delete current credential
                    cursor.execute(f"DELETE FROM xbox_credential WHERE client_id={existing_credentials[0]}")
                    # Insert a new credential record.
                    cursor.execute(f"INSERT INTO xbox_credential (client_id, client_secret, token_type, expires_in, scope, access_token, refresh_token, user_id, issued) VALUES('{client_id}', '{client_secret}', '{tokens['token_type']}', {tokens['expires_in']}, '{tokens['scope']}', '{tokens['access_token']}', '{tokens['refresh_token']}', '{tokens['user_id']}', '{tokens['issued']}')")
        print("20")
        # and link oauth2 login
        update.message.reply_text(f"Your Xbox credentials have been validated! You can use the /xbox_status command now")
    else:
        # refresh tokens
        tokens = {
            "token_type": existing_credentials[3],
            "expires_in": existing_credentials[4],
            "scope": existing_credentials[5],
            "access_token": existing_credentials[6],
            "refresh_token": existing_credentials[7], 
            "user_id": existing_credentials[8], 
            "issued": existing_credentials[9]
            }
        with ClientSession() as session:
            auth_mgr = AuthenticationManager(
                session, client_id, client_secret, XBOX_AUTH_REDIRECT_URI
            )
            auth_mgr.oauth = OAuth2TokenResponse.parse_raw(tokens)
            try:
                auth_mgr.refresh_tokens()
            except:
                print("Error refreshing tokens")

            tokens = auth_mgr.oauth.dict()

            with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"UPDATE xbox_credential SET token_type = '{tokens['token_type']}', expires_in = {tokens['expires_in']}, scope = '{tokens['scope']}', access_token = '{tokens['access_token']}, refresh_token = '{tokens['refresh_token']}', user_id = '{tokens['user_id']}', issued = '{tokens['issued']}' WHERE client_id = '{existing_credentials[1]}'")


        update.message.reply_text(f"The credentials you entered already exist in the system and have already been validated!")

    return ConversationHandler.END

def playstation_credentials_setup(update, context):
    """Asks the user privately for the Playstation."""
    if update['message'].from_user.id in ADMIN_LIST:
        try:
            update['message'].from_user.send_message(
                text="Please follow the following instructions to obtain your PSN npsso and then reply with that npsso in a message:\n\n1.Login into your <a href='https://my.playstation.com/'>My PlayStation</a> account.\n2.In another tab, go to <a href='https://ca.account.sony.com/api/v1/ssocookie'>https://ca.account.sony.com/api/v1/ssocookie</a>\n3.Here you will find the npsso code. Only copy the code (without the quotation marks) itself and paste it in a message to the bot.",
                parse_mode=ParseMode.HTML
            )
            return TYPING_NPSSO
        except:
            update.message.reply_text(text=f"You need to start the bot privately first! Click <a href='{BOT_LINK}'>here</a> and click on start/restart. Then try this command again.", parse_mode=ParseMode.HTML)
            return ConversationHandler.END

def store_playstation_npsso(update, context):
    """Stores the user provided Playstation npsso."""
    npsso = update.message.text
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM playstation_credential")
            existing_credentials = cursor.fetchone()
            if existing_credentials and existing_credentials[1] == npsso:
                update.message.reply_text(f"The npsso code provided has already been previously stored and validated!")
            else:
                if existing_credentials:
                    cursor.execute(f"DELETE FROM playstation_credential WHERE client_id={existing_credentials[0]}")
                
                cursor.execute(f"INSERT INTO playstation_credential (npsso) VALUES('{npsso}')")
                update.message.reply_text("The npsso code has been successfully stored.")
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text("The message you entered did not register as a valid response to the query. Try running the original command again if you want to retry the process.")
    return ConversationHandler.END




