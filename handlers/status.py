import json
import datetime
import requests
import humanize
import os
from general import values
from general.values import STATUS_DB


def add_status_user(update, context):
    if not context.args:
        update.message.reply_text("You need to provide arguments to this command! See /help")
        return
    status_content = None
    group_id = str(update.effective_chat.id)
    with open(STATUS_DB, "r") as f:
        status_content = json.load(f)
        users = set([])
        for user in context.args:
            tokens = user.split(",")
            users.add((tokens[0].strip(), int(tokens[1])))
        if not status_content.get(group_id):
            status_content[group_id] = {}
        for nickname, xuid in users:
            status_content[group_id][nickname] = xuid

    with open(STATUS_DB, "w") as f:
        json.dump(status_content, f, indent=4)

    update.message.reply_text("Done! The new user(s) have been added.")


def del_status_user(update, context):
    if not context.args:
        update.message.reply_text("You need to provide arguments to this command! See /help")
        return
    status_content = None
    group_id = str(update.effective_chat.id)
    with open(STATUS_DB, "r") as f:
        status_content = json.load(f)
        users = []
        if not status_content.get(group_id):
            status_content[group_id] = {}
        else:
            for key in context.args:
                if status_content[group_id].get(key):
                    del status_content[group_id][key]

    with open(STATUS_DB, "w") as f:
        json.dump(status_content, f, indent=4)

    update.message.reply_text("Done! The new user(s) have been deleted.")


def list_status_users(update, context):
    listed_status_users = "The users in the status list are:"
    group_id = str(update.effective_chat.id)
    with open(STATUS_DB, "r") as f:
        status_content = json.load(f)
        if status_content.get(group_id) and len(status_content[group_id]) != 0:
            for nickname in status_content[group_id]:
                listed_status_users += f"\n{nickname}, {status_content[group_id][nickname]}"
            listed_status_users = listed_status_users[:-1]
        else:
            listed_status_users += " No users have been set."
    update.message.reply_text(listed_status_users)


def status(update, context):
    online_statuses = ""
    group_id = str(update.effective_chat.id)
    with open(STATUS_DB, "r") as f:
        status_content = json.load(f)
        if status_content.get(group_id) and len(status_content[group_id]) != 0:
            for friend in status_content[group_id]:
                resp = requests.get("https://xapi.us/v2/{}/presence".format(
                    status_content[group_id][friend]),
                    headers={"X-AUTH":os.environ.get("XPAI_API_KEY")})
                if resp.status_code != 200:
                    update.message.reply_text("Something went wrong with the API.")
                resp = json.loads(resp.text)
                if resp["state"] == "Offline":
                    online_statuses += f"{values.OFFLINE_EMOJI} {friend}: {resp['state']}\nLast seen: "
                    if resp.get("cloaked"):
                        online_statuses += "Unknown\n\n"
                    else:
                        last_seen = humanize.naturaltime(datetime.datetime.fromisoformat(resp["lastSeen"]["timestamp"][:-5]) - datetime.datetime.utcnow())
                        last_seen = last_seen.replace("from now", "ago")
                        online_statuses += f"{last_seen}\n\n"
                else:
                    online_statuses += f"{values.ONLINE_EMOJI} {friend}: {resp['state']}\nPlaying: "
                    if resp.get("cloaked"):
                        online_statuses += "Unknown\n\n"
                    else:
                        online_statuses += f"{resp['devices'][0]['titles'][0]['name']}\n\n"
    update.message.reply_text(online_statuses)