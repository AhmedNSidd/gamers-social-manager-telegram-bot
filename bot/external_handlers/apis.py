import asyncio
import datetime
import humanize
import json
import psnawp_api
import requests

from general import values
from general.db import DBConnection
from models.player_presence import PlayerPresence
from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.api.provider.presence import PresenceLevel
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from xbox.webapi.scripts import REDIRECT_URI


class PsnApi:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(PsnApi)
            return cls.instance
        return cls.instance

    def __init__(self):
        self.client = psnawp_api.psnawp.PSNAWP(self._get_psn_npsso())
        self._check_credentials_expiry()

    def _get_psn_npsso(self):
        credentials = DBConnection().find_one("credentials",
                                              {"platform": "psn"})
        if not credentials:
            raise Exception("PSN credentials have not been set")

        return credentials["npsso"]

    def _check_credentials_expiry(self):
        days_to_expire = int(self.client.authenticator.oauth_token_response['refresh_token_expires_in']/86400)
        if days_to_expire <= 0:
            raise Exception("PSN credentials need to be renewed")
        if days_to_expire <= 7:
            for admin_id in values.ADMIN_LIST:
                requests.post(
                    url=f"https://api.telegram.org/bot{values.TOKEN}/sendMessage",
                    data={
                        "chat_id": admin_id,
                        "text": "Warning: The Playstation npsso is expiring "
                        "in less than 7 days. Please update it soon."
                    }
                )

    async def get_account_id_from_online_id(self, session, psn_online_id):
        """
        Given a psn_online_id, function returns the psn_account_id associated
        with that online ID.
        """
        headers={  
            "Authorization": f"Bearer {self.client.authenticator.obtain_fresh_access_token()}",
        }
        params={"fields": "accountId,onlineId,currentOnlineId"}
        url = f"https://us-prof.np.community.playstation.net/userProfile/v1/users/{psn_online_id}/profile2"
        async with session.get(url, headers=headers, params=params) as res:
            res.raise_for_status()
            return int((await res.json())["profile"]["accountId"])

    async def get_players_presences(self, session, account_ids, online_ids):
        """
        This function takes in a list of psn_ids that contains both the account
        id (which is a unique number identifier) and the online id (which is
        a unique string username) for all the users who's status needs to be
        returned.
        """
        if not account_ids or not online_ids:
            return []
        headers = {"Authorization": f"Bearer {self.client.authenticator.obtain_fresh_access_token()}"}
        params = {"type": "primary"}
        tasks = []
        for i in range(len(account_ids)):
            url = f"{psnawp_api.user.User.base_uri}/{account_ids[i]}/basicPresences" 
            tasks.append(asyncio.ensure_future(self._request_presence(
                                session, url, headers, params, online_ids[i])))
        return await asyncio.gather(*tasks)

    async def _request_presence(self, session, url, headers, params, online_id):
        if not online_id:
            return None
        async with session.get(url, headers=headers, params=params) as res:
            res = await res.json()
            if "basicPresence" in res:
                res = res["basicPresence"]
            return PlayerPresence(online_id, "PSN", 
                                PsnApi._parse_platform(res),
                                PsnApi._parse_player_state(res),
                                PsnApi._parse_game_title(res),
                                PsnApi._parse_last_seen(res))

    @staticmethod
    def _parse_platform(resp):
        if "primaryPlatformInfo" in resp and "platform" in resp["primaryPlatformInfo"]:
            return resp["primaryPlatformInfo"]["platform"]

    @staticmethod
    def _parse_player_state(resp):
        if resp["availability"] == "availableToPlay":
            return PlayerPresence.ONLINE
        elif resp["availability"] == "doNotDisturb":
            return PlayerPresence.DO_NOT_DISTURB
        elif resp["availability"] == "unavailable":
            return PlayerPresence.OFFLINE
        return PlayerPresence.UNKNOWN

    @staticmethod
    def _parse_game_title(resp):
        if "gameTitleInfoList" in resp:
            for game in resp["gameTitleInfoList"]:
                if game["launchPlatform"] == resp["primaryPlatformInfo"]["platform"]:
                    return game["titleName"]

    @staticmethod
    def _parse_last_seen(resp):
        if "primaryPlatformInfo" in resp or "lastAvailableDate" in resp:
            if "primaryPlatformInfo" in resp and "lastOnlineDate" in resp["primaryPlatformInfo"]:
                last_seen = humanize.naturaltime(datetime.datetime.fromisoformat(resp["primaryPlatformInfo"]["lastOnlineDate"][:23]) - datetime.datetime.utcnow())
            elif "lastAvailableDate" in resp:
                last_seen = humanize.naturaltime(datetime.datetime.fromisoformat(resp["lastAvailableDate"][:23]) - datetime.datetime.utcnow())
            last_seen = last_seen.replace("from now", "ago")
            return last_seen


class XboxLiveApi:
    # highest number is highest priority
    device_priority_list = {
        "Unknown": 0,
        "All": 1,
        "Nintendo": 2,
        "PlayStation": 3,
        "iOS": 4,
        "Android": 5,
        "Win32": 6,
        "WindowsOneCore": 7,
        "XboxOne": 8,
        "Scarlett": 9,
    }

    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(XboxLiveApi)
            return cls.instance
        return cls.instance

    def __init__(self):
        self._initialize_credentials()
        self._check_expiry()

    def _initialize_credentials(self):
        self.credentials = DBConnection().find_one("credentials",
                                                   {"platform": "xbox"})
        if not self.credentials:
            raise Exception("Xbox Live credentials have not been set")
    
    def _check_expiry(self):
        days_to_expire = (values.XBOX_CLIENT_SECRET_EXPIRY_DATE - datetime.date.today()).days
        if days_to_expire <= 0:
            raise Exception("Xbox Live credentials need to be renewed")
        elif days_to_expire < 7:
            for admin_id in values.ADMIN_LIST:
                requests.post(
                    url=f"https://api.telegram.org/bot{values.TOKEN}/sendMessage",
                    data={
                        "chat_id": admin_id,
                        "text": "Warning: The Xbox Secret Key is expiring in "
                        "less than 7 days. Please update it soon."
                    }
                )
    
    async def _refresh_tokens(self, auth_mgr):
        auth_mgr.oauth = OAuth2TokenResponse.parse_raw(
            json.dumps(self.credentials["tokens"]))
        try:
            await auth_mgr.refresh_tokens()
        except:
            raise Exception("Error: Could not refresh tokens.")

        self.credentials["tokens"] = json.loads(auth_mgr.oauth.json())
        DBConnection().update_one(
            "credentials",
            {"platform": "xbox"},
            {"$set": {
                "tokens": self.credentials["tokens"]
            }}
        )

    async def get_account_id_from_gamertag(self, session, gamertag):
        """
        Given an xbox gamertag, function returns the Xbox account ID associated
        with that gamertag.
        """
        auth_mgr = AuthenticationManager(
            session, self.credentials["client_id"],
            self.credentials["client_secret"], REDIRECT_URI
        )
        await self._refresh_tokens(auth_mgr)
        xbl_client = XboxLiveClient(auth_mgr)
        id = (await xbl_client.profile.get_profile_by_gamertag(gamertag)).profile_users[0].id
        return int(id)

    async def get_players_presences(self, session, account_ids, gamertags):
        """
        This function takes in a list of xbox_ids that contains both the account
        id (which is a unique number identifier) and the gamertag (which is
        a unique string username) for all the users who's status needs to be
        returned.
        """
        # problem, we'll get input like [34128349, None, 3445859285]
        # and we want2 return [PP(), None, PP()]
        players_presences = []
        auth_mgr = AuthenticationManager(
            session, self.credentials["client_id"],
            self.credentials["client_secret"], REDIRECT_URI
        )
        await self._refresh_tokens(auth_mgr)
        xbl_client = XboxLiveClient(auth_mgr)
        resp = await xbl_client.session.post(
            "https://userpresence.xboxlive.com/users/batch",
            json={
                "users": [id for id in account_ids if id],
                "level": PresenceLevel.ALL,
            }, headers={
                "x-xbl-contract-version": "3",
                "Accept": "application/json"
            }
        )
        resp.raise_for_status()
        resp = await resp.json()
        presences = []
        resp_ctr = 0
        for account_id in account_ids:
            if account_id:
                presences.append(resp[resp_ctr])
                resp_ctr += 1
            else:
                presences.append(None)
        for x in range(len(presences)):
            if presences[x]:
                main_device = XboxLiveApi._parse_main_device(presences[x])
                player = PlayerPresence(gamertags[x], "XBOXLIVE",
                    XboxLiveApi._parse_platform(presences[x], main_device),
                    XboxLiveApi._parse_player_state(presences[x]),
                    XboxLiveApi._parse_game_title(presences[x], main_device),
                    XboxLiveApi._parse_last_seen(presences[x])
                )  
                players_presences.append(player)
            else:
                players_presences.append(None)

        return players_presences

    @staticmethod
    def _parse_main_device(resp):
        """
        This function returns the user's main device. The main device is
        defined as the device having highest priority for presence. For
        example, the user probably wants to know the status of their Xbox
        Series X rather than the status of their Android device.

        The priority is defined as a class variable in this api.
        """
        if not resp["state"] == "Offline" and "devices" in resp: # Either Online or Away
            prioritized_devices = sorted(resp["devices"], key=lambda device: XboxLiveApi.device_priority_list[device["type"]])
            return prioritized_devices[0]
        elif "lastSeen" in resp and "deviceType" in resp["lastSeen"]:
            return resp["lastSeen"]["deviceType"]

    @staticmethod
    def _parse_platform(resp, main_device):
        if not resp["state"] == "Offline": # Either Online or Away
            if main_device:
                return main_device["type"]
        elif "lastSeen" in resp and "deviceType" in resp["lastSeen"]:
            return resp["lastSeen"]["deviceType"]

    @staticmethod
    def _parse_player_state(resp):
        if resp["state"] == "Online":
            return PlayerPresence.ONLINE
        elif resp["state"] == "Away":
            return PlayerPresence.AWAY
        elif resp["state"] == "Offline":
            return PlayerPresence.OFFLINE
        return PlayerPresence.UNKNOWN

    @staticmethod
    def _parse_game_title(resp, main_device):
        if "lastSeen" in resp and "titleName" in resp["lastSeen"]: # user state is offline
            return resp["lastSeen"]["titleName"]
        else:
            if main_device:
                for title in main_device["titles"]:
                    if title["placement"] == "Full":
                        return f'{title["name"]}' if title["name"] != "Online" else None
                return main_device["titles"][0]["name"] if main_device["titles"][0]["name"] != "Online" else None

    @staticmethod
    def _parse_last_seen(resp):
        if "lastSeen" in resp:
            last_seen = humanize.naturaltime(datetime.datetime.fromisoformat(resp["lastSeen"]["timestamp"][:23]) - datetime.datetime.utcnow())
            last_seen = last_seen.replace("from now", "ago")
            return last_seen
