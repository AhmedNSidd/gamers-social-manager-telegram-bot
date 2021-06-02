import requests
import psycopg2
import os
from general.utils import create_sql_array
from external_handlers.xbox_api import XboxApi
import urllib.parse as urlparse


url = urlparse.urlparse(os.environ['DATABASE_URL'])

def add_status_user(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            users = set([])
            for user in context.args:
                tokens = user.split(",")
                users.add((tokens[0].strip(), int(tokens[1])))
            cursor.execute('SELECT name, xuid FROM status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                # Create a local copy of our updated list of xuids and names.
                new_users = [user[0] for user in users]
                new_xuids = [user[1] for user in users]

                # Build up a query to insert new users as a new record in the table
                query = f"INSERT INTO status (id, name, xuid) VALUES({group_id}, {create_sql_array(new_users)}, {create_sql_array(new_xuids)})"
                cursor.execute(query)
            else:
                # Create a local copy of our updated list of xuids and names.
                new_users = curr_record[0] + [user[0] for user in users]
                new_xuids = curr_record[1] + [user[1] for user in users]

                # Build up a query to insert new users plus any pre-existing ones
                query = f"UPDATE status SET name = {create_sql_array(new_users)}, xuid = {create_sql_array(new_xuids)} WHERE id = {group_id}"
                cursor.execute(query)

        update.message.reply_text("Done! The new user(s) have been added.")


def del_status_user(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT name, xuid FROM status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                query = f"INSERT INTO status (id) VALUES({group_id})"
                cursor.execute(query)
            else:
                new_users = curr_record[0]
                new_xuids = curr_record[1]
                for user in context.args:
                    try:
                        index = new_users.index(user)
                        new_users.pop(index)
                        new_xuids.pop(index)
                    except ValueError:
                        continue
                    
                query = f"UPDATE status SET name = {create_sql_array(new_users)}, xuid = {create_sql_array(new_xuids)} WHERE id = {group_id}"
                cursor.execute(query)

        update.message.reply_text("Done! The new user(s) have been deleted.")


def list_status_users(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        listed_status_users = "The users in the status list are:"
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT name, xuid FROM status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                listed_status_users += " No users have been set."
            else:
                for x in range(len(curr_record[0])):
                    listed_status_users += f"\n- {curr_record[0][x]}, {curr_record[1][x]}"  
        update.message.reply_text(listed_status_users)


def status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        players = []
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT name, xuid FROM status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                update.message.reply_text("No users have been set to show status of.")
            else:
                for x in range(len(curr_record[0])):
                    try:
                        user = XboxApi.get_player(curr_record[1][x], curr_record[0][x])
                        players.append(str(user))
                    except requests.HTTPError:
                        update.message.reply_text("Something went wrong with the API.")
                    
                players.sort()

        update.message.reply_text("".join(players))
