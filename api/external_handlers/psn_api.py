import asyncio
import datetime
import humanize
import psnawp_api
import requests

from common import values
from common.db import DBConnection
from models.player_presence import PlayerPresence


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

