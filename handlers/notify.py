import json
from os.path import isfile
from general.values import NOTIFY_DB


def set_notify_msg(update, context):
    if not context.args:
        update.message.reply_text("You need to provide arguments to this command! See /help")
        return
    group_id = str(update.effective_chat.id)
    notify_content = None
    if not isfile(NOTIFY_DB):
        f = open(NOTIFY_DB, "w")
        f.write(json.dumps({}))
        f.close()
    with open(NOTIFY_DB, "r") as f:
        notify_content = json.load(f)
        new_notify_msg = " ".join(context.args)
        if notify_content.get(group_id):
            notify_content[group_id]["message"] = new_notify_msg
        else:
            notify_content[group_id] = {
                "message": new_notify_msg,
                "tagged": [],
            }

    with open(NOTIFY_DB, "w") as f:
        json.dump(notify_content, f, indent=4)

    update.message.reply_text("Done! The new notify message has been set.")

def add_notify_user(update, context):
    if not context.args:
        update.message.reply_text("You need to provide arguments to this command! See /help")
        return
    notify_content = None
    group_id = str(update.effective_chat.id)
    if not isfile(NOTIFY_DB):
        f = open(NOTIFY_DB, "w")
        f.write(json.dumps({}))
        f.close()
    with open(NOTIFY_DB, "r") as f:
        notify_content = json.load(f)
        if notify_content.get(group_id):
            notify_content[group_id]["tagged"] = list(set(notify_content[group_id]["tagged"] + context.args))
        else:
            notify_content[group_id] = {
                "message": "",
                "tagged": list(set(context.args)),
            }

    with open(NOTIFY_DB, "w") as f:
        json.dump(notify_content, f, indent=4)

    update.message.reply_text("Done! The new user(s) have been added.")


def del_notify_user(update, context):
    if not context.args:
        update.message.reply_text("You need to provide arguments to this command! See /help")
        return
    notify_content = None
    group_id = str(update.effective_chat.id)
    if not isfile(NOTIFY_DB):
        f = open(NOTIFY_DB, "w")
        f.write(json.dumps({}))
        f.close()
    with open(NOTIFY_DB, "r") as f:
        notify_content = json.load(f)
        if notify_content.get(group_id):
            for user in context.args:
                if user in notify_content[group_id]["tagged"]: 
                    notify_content[group_id]["tagged"].remove(user)
        else:
            notify_content[group_id] = {
                "message": "",
                "tagged": [],
            }

    with open(NOTIFY_DB, "w") as f:
        json.dump(notify_content, f, indent=4)

    update.message.reply_text("Done! The new user(s) have been deleted.")

def list_notify_users(update, context):
    listed_notify_users = "The users to notify are:"
    group_id = str(update.effective_chat.id)
    if not isfile(NOTIFY_DB):
        f = open(NOTIFY_DB, "w")
        f.write(json.dumps({}))
        f.close()
    with open(NOTIFY_DB, "r") as f:
        notify_content = json.load(f)
        if notify_content.get(group_id) and notify_content[group_id]["tagged"]:
            for user in notify_content[group_id]["tagged"]:
                listed_notify_users += f" {user},"
            listed_notify_users = listed_notify_users[:-1]
        else:
            listed_notify_users += " No users have been set."
    update.message.reply_text(listed_notify_users)


def list_notify_msg(update, context):
    listed_notify_msg = "The message to notify is:"
    group_id = str(update.effective_chat.id)
    if not isfile(NOTIFY_DB):
        f = open(NOTIFY_DB, "w")
        f.write(json.dumps({}))
        f.close()
    with open(NOTIFY_DB, "r") as f:
        notify_content = json.load(f)
        if notify_content.get(group_id) and notify_content[group_id]["message"] != "":
            listed_notify_msg += " '" + notify_content[group_id]["message"] + "'"
        else:
            listed_notify_msg += " No message has been set."
    update.message.reply_text(listed_notify_msg)
    

def notify(update, context):
    notify_users_and_msg = ""
    group_id = str(update.effective_chat.id)
    if not isfile(NOTIFY_DB):
        f = open(NOTIFY_DB, "w")
        f.write(json.dumps({}))
        f.close()
    with open(NOTIFY_DB, "r") as f:
        notify_content = json.load(f)
        if notify_content.get(group_id):
            for user in notify_content[group_id]["tagged"]:
                notify_users_and_msg += "@" + user + " "
            notify_users_and_msg += notify_content[group_id]["message"]
    if notify_users_and_msg == "":
        update.message.reply_text("You don't have any users or a message to set for notify.")
    else:
        update.message.reply_text(notify_users_and_msg)