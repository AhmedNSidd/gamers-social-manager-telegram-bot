import datetime
import humanize
import os
import psycopg2
import requests
import urllib.parse as urlparse

from aiohttp import ClientSession
from general import values
from models.player import Player
from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.api.provider.presence import PresenceLevel
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse


url = urlparse.urlparse(os.environ['DATABASE_URL'])

class XboxApi(object):
    async def __init__(self, client_id, client_secret, tokens):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tokens = tokens
        self._check_expiry()
        
    async def get_players(self, ids, names):
        async with ClientSession() as session:
            auth_mgr = AuthenticationManager(
                session, self.client_id, self.client_secret, 
            )

            try:
                auth_mgr.oauth = OAuth2TokenResponse.parse_raw(self.tokens)
            except:
                raise Exception('Error: Tokens could not be parsed.')

            try:
                await auth_mgr.refresh_tokens()
            except:
                raise Exception("Error: Could not refresh tokens.")

            self.tokens = auth_mgr.oauth.dict()
            
            with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"UPDATE xbox_credential SET token_type = '{self.tokens['token_type']}', expires_in = {self.tokens['expires_in']}, scope = '{self.tokens['scope']}', access_token = '{self.tokens['access_token']}, refresh_token = '{self.tokens['refresh_token']}', user_id = '{self.tokens['user_id']}', issued = '{self.tokens['issued']}' WHERE client_id = '{self.client_id}'")

            xbl_client = XboxLiveClient(auth_mgr)

            resp = await xbl_client.presence.get_presence_batch(ids, presence_level=PresenceLevel.ALL)
            player_list = []

            for x in range(len(resp)):
                is_user_online = XboxApi._parse_is_online(resp[x])
                player = Player(ids[x], names[x], is_user_online,
                                XboxApi._parse_current_title(resp[x]) if is_user_online else None,
                                XboxApi._parse_last_seen(resp) if "lastSeen" in resp else None)
                player_list.append(player)

            return player_list

    def _check_expiry(self):
        if (values.XBOX_CLIENT_SECRET_EXPIRY_DATE - datetime.date.today()).days < 7:
            for admin_id in values.ADMIN_LIST:
                requests.post(url=f"https://api.telegram.org/bot{values.TOKEN}/sendMessage",
                              data={"chat_id": admin_id,
                              "text": "Warning: The Xbox Secret Key is expiring in less than 7 days. Please update it soon."})

    @staticmethod
    def _parse_is_online(resp):
        return resp["state"] == "Online"

    @staticmethod
    def _parse_current_title(resp):
        for title in resp["devices"][0]["titles"]:
            if title["placement"] == "Full":
                return title["name"]
        return resp['devices'][0]['titles'][0]['name']

    @staticmethod
    def _parse_last_seen(resp):
        last_seen = humanize.naturaltime(datetime.datetime.fromisoformat(resp["lastSeen"]["timestamp"][:23]) - datetime.datetime.utcnow())
        last_seen = last_seen.replace("from now", "ago")

        return last_seen
