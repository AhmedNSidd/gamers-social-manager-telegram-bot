import json
import requests
import os
from general.values import STATUS_DB
from external_handlers.xbox_api import XboxApi


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
    players = []
    group_id = str(update.effective_chat.id)
    with open(STATUS_DB, "r") as f:
        status_content = json.load(f)
        if status_content.get(group_id) and len(status_content[group_id]) != 0:
            for name in status_content[group_id]:
                try:
                    user = XboxApi.get_player(status_content[group_id][name], name)
                    players.append(str(user))
                except requests.HTTPError:
                    update.message.reply_text("Something went wrong with the API.")
            players.sort()

    update.message.reply_text("".join(players))
