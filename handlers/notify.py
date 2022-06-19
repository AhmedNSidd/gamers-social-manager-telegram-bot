import psycopg2
import os
from general.utils import create_sql_array
import urllib.parse as urlparse


url = urlparse.urlparse(os.environ['DATABASE_URL'])

def set_notify_msg(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            new_notify_msg = " ".join(context.args)
            cursor.execute('SELECT 1 FROM notifications WHERE id = {}'.format(group_id))
            group_exists = cursor.fetchone()
            if group_exists:
                cursor.execute("UPDATE notifications SET message = '{}' WHERE id = {}".format(new_notify_msg, group_id))
            else:
                cursor.execute("INSERT INTO notifications (id, message) VALUES({}, '{}')".format(group_id, new_notify_msg))

        update.message.reply_text("Done! The new notify message has been set.")


def add_notify_user(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            # See if a record for the group already exists in the notifications table
            cursor.execute("SELECT 1 FROM notifications WHERE id = {}".format(group_id))
            group_exists = cursor.fetchone()
            if group_exists:
                # Get a list of pre-existing users stored in the record
                cursor.execute("SELECT users from notifications where id = {}".format(group_id))
                users = cursor.fetchone()
                users = set(users[0] + context.args) if users else set(context.args)

                # Build up a query to insert new users plus any pre-existing ones
                query = f"UPDATE notifications SET users = {create_sql_array(list(users))} WHERE id = {group_id}"
                cursor.execute(query)
            else:
                # Build up a query to insert new users as a new record in the table
                query = f"INSERT INTO notifications (id, users) VALUES({group_id}, {create_sql_array(context.args)})"
                cursor.execute(query)

        update.message.reply_text("Done! The new user(s) have been added.")


def del_notify_user(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            # See if a record for the group already exists in the notifications table
            cursor.execute("SELECT 1 FROM notifications WHERE id = {}".format(group_id))
            group_exists = cursor.fetchone()
            if group_exists:
                # Get the current list of users from the record
                cursor.execute("SELECT users FROM notifications WHERE id = {}".format(group_id))
                curr_users = cursor.fetchone()
                if not curr_users:
                    # If no users exist, just let the user know and end flow
                    update.message.reply_text("There are no users available to delete.")
                    return
                
                # Create a local copy of updated user list
                curr_users = curr_users[0]
                for user in context.args:
                    try:
                        curr_users.remove(user)
                    except ValueError:
                        continue
                
                # Build up a query to delete users from the table
                query = f"UPDATE notifications SET users = {create_sql_array(curr_users)} WHERE id = {group_id}"
                cursor.execute(query)  
            else:
                # If a record doesn't exist, then just create an empty record for the group
                cursor.execute("INSERT INTO notifications (id) VALUES({})".format(group_id))
                update.message.reply_text("There are no users available to delete.")
                return

        update.message.reply_text("Done! The new user(s) have been deleted.")


def list_notify_users(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        listed_notify_users = "The users to notify are:"
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute("SELECT users FROM notifications WHERE id = {}".format(group_id))
            curr_users = cursor.fetchone()
            if curr_users:
                for user in curr_users[0]:
                    listed_notify_users += f"\n- {user}"
            else:
                listed_notify_users += " No users have been set." 

        update.message.reply_text(listed_notify_users)


def list_notify_msg(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        listed_notify_msg = "The message to notify is:"
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute("SELECT message FROM notifications WHERE id = {}".format(group_id))
            curr_msg = cursor.fetchone()
            if not curr_msg or not curr_msg[0]:
                listed_notify_msg += " No message has been set."
            else:
                listed_notify_msg += " '" + curr_msg[0] + "'"

        update.message.reply_text(listed_notify_msg)


def notify(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        notify_users_and_msg = ""
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute("SELECT message, users FROM notifications WHERE id = {}".format(group_id))
            record = cursor.fetchone()
            if record:
                for user in record[1]:
                    notify_users_and_msg += f"@{user} "
                if record[0]:
                    notify_users_and_msg += f"{record[0]}"
                update.message.reply_text(notify_users_and_msg)
            else:
                update.message.reply_text("You don't have any users or a message to set for notify.")
