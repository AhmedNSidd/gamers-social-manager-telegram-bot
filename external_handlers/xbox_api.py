import datetime
import humanize
import json
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
from xbox.webapi.scripts import REDIRECT_URI


url = urlparse.urlparse(os.environ['DATABASE_URL'])

class XboxApi(object):
    def __init__(self, client_id, client_secret, tokens):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tokens = tokens
        self._check_expiry()
        
    async def get_players(self, gamertags):
        async with ClientSession() as session:
            auth_mgr = AuthenticationManager(
                session, self.client_id, self.client_secret, REDIRECT_URI
            )
            auth_mgr.oauth = OAuth2TokenResponse.parse_raw(json.dumps(self.tokens))

            try:
                await auth_mgr.refresh_tokens()
            except:
                raise Exception("Error: Could not refresh tokens.")

            self.tokens = auth_mgr.oauth.dict()
            
            with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"UPDATE xbox_credential SET token_type = '{self.tokens['token_type']}', expires_in = {self.tokens['expires_in']}, scope = '{self.tokens['scope']}', access_token = '{self.tokens['access_token']}', refresh_token = '{self.tokens['refresh_token']}', user_id = '{self.tokens['user_id']}', issued = '{self.tokens['issued']}' WHERE client_id = '{self.client_id}'")

            xbl_client = XboxLiveClient(auth_mgr)
            ids = [(await xbl_client.profile.get_profile_by_gamertag(gamertag)).profile_users[0].id for gamertag in gamertags]
            resp = await xbl_client.session.post(
                "https://userpresence.xboxlive.com/users/batch",
                json={
                    "users": ids,
                    "level": PresenceLevel.ALL,
                }, headers={
                    "x-xbl-contract-version": "3",
                    "Accept": "application/json"
                }
            )
            resp.raise_for_status()
            resp = await resp.json()
            player_list = []
            for x in range(len(resp)):
                is_user_online = XboxApi._parse_is_online(resp[x])
                player = Player(gamertags[x], is_user_online,
                                XboxApi._parse_current_title(resp[x]) if is_user_online else None,
                                XboxApi._parse_last_seen(resp[x]) if "lastSeen" in resp[x] else None)
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
                return f'{title["name"]} ({resp["devices"][0]["type"]})' if title["name"] != "Online" else None
        return f"{resp['devices'][0]['titles'][0]['name']} ({resp['devices'][0]['type']})" if resp['devices'][0]['titles'][0]['name'] != "Online" else None

    @staticmethod
    def _parse_last_seen(resp):
        last_seen = humanize.naturaltime(datetime.datetime.fromisoformat(resp["lastSeen"]["timestamp"][:23]) - datetime.datetime.utcnow())
        last_seen = last_seen.replace("from now", "ago")
        if "titleName" in resp["lastSeen"]:
            last_seen += f" on \"{resp['lastSeen']['titleName']}\""
        return last_seen
