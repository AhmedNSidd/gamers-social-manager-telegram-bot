import datetime
import humanize
import json
import os
import requests
from models.xbox_user import XboxUser

class XboxApi(object):
    @staticmethod
    def get_player(id, name):
        resp = requests.get("https://xapi.us/v2/{}/presence".format(id),
            headers={"X-AUTH":os.environ.get("XPAI_API_KEY")})

        if resp.status_code != 200:
            raise requests.HTTPError(id)

        resp = json.loads(resp.text)
        is_user_online = XboxApi._parse_is_online(resp)

        return XboxUser(id,
            name,
            is_user_online,
            XboxApi._parse_current_title(resp) if is_user_online else None,
            XboxApi._parse_last_seen(resp) if "lastSeen" in resp else None)

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
        last_seen = humanize.naturaltime(datetime.datetime.fromisoformat(resp["lastSeen"]["timestamp"][:25]) - datetime.datetime.utcnow())
        last_seen = last_seen.replace("from now", "ago")

        return last_seen
