import datetime
import humanize
import requests

from general import values
from models.player import Player
from psnawp_api import psnawp


class PlaystationApi:
    # REVIEW: To implement object class here or not? why or why not?

    def __init__(self, npsso) -> None:
        # REVIEW: Is client an appropriate name for this obj. variable?
        self.client = psnawp.PSNAWP(npsso)
        self._check_expiry()

    def get_players(self, online_ids):
        player_list = []
        for online_id in online_ids[::-1]:
            resp = self.client.user(online_id=online_id).get_presence()
            is_user_online = PlaystationApi._parse_is_online(resp)
            player = Player(online_id, is_user_online,
                PlaystationApi._parse_current_title(resp) if is_user_online else None,
                PlaystationApi._parse_last_seen(resp) if not is_user_online else None
            )
            player_list.append(player)

        return player_list

    def _check_expiry(self):
        if self.client.authenticator.oauth_token_response['refresh_token_expires_in'] <= 604800:
            for admin_id in values.ADMIN_LIST:
                requests.post(url=f"https://api.telegram.org/bot{values.TOKEN}/sendMessage",
                              data={"chat_id": admin_id,
                              "text": "Warning: The Playstation npsso is expiring in less than 7 days. Please update it soon."})

    # REVIEW: I don't see why these shouldn't be static methods
    # but at the same time, I see no use case for these methods
    # being called outside of inside this API. 
    # 
    # Should private helper methods be static?
    @staticmethod
    def _parse_is_online(resp):
        return resp["availability"] == "availableToPlay"

    @staticmethod
    def _parse_current_title(resp):
        if "gameTitleInfoList" in resp:
            return f"{resp['gameTitleInfoList'][0]['titleName']} ({resp['primaryPlatformInfo']['platform']})"
        elif resp.get("primaryPlatformInfo"):
            return f"{resp['primaryPlatformInfo'].get('platform', 'Unknown')} Main Menu"

    @staticmethod
    def _parse_last_seen(resp):
        if not 'lastAvailableDate' in resp:
            return None
        last_seen = humanize.naturaltime(datetime.datetime.fromisoformat(resp["lastAvailableDate"][:23]) - datetime.datetime.utcnow())
        last_seen = last_seen.replace("from now", "ago")

        return last_seen
