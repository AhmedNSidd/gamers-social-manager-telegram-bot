import asyncio
import os
import psycopg2
import urllib.parse as urlparse

from general.utils import create_sql_array
from external_handlers.xbox_api import XboxApi
from external_handlers.playstation_api import PlaystationApi


url = urlparse.urlparse(os.environ['DATABASE_URL'])

def add_xbox_status_user(update, context):
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
            cursor.execute('SELECT names, xbox_ids FROM xbox_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                # Create a local copy of our updated list of xbox ids and names.
                new_users = [user[0] for user in users]
                new_xbox_ids = [user[1] for user in users]

                # Build up a query to insert new users as a new record in the table
                query = f"INSERT INTO xbox_status (id, names, xbox_ids) VALUES({group_id}, {create_sql_array(new_users)}, {create_sql_array(new_xbox_ids)})"
                cursor.execute(query)
            else:
                # Create a local copy of our updated list of xbox ids and names.
                new_users = curr_record[0] + [user[0] for user in users]
                new_xbox_ids = curr_record[1] + [user[1] for user in users]

                # Build up a query to insert new users plus any pre-existing ones
                query = f"UPDATE xbox_status SET names = {create_sql_array(new_users)}, xbox_ids = {create_sql_array(new_xbox_ids)} WHERE id = {group_id}"
                cursor.execute(query)

    update.message.reply_text("Done! The new user(s) have been added.")


def del_xbox_status_user(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT names, xbox_ids FROM xbox_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                query = f"INSERT INTO xbox_status (id) VALUES({group_id})"
                cursor.execute(query)
            else:
                new_users = curr_record[0]
                new_xbox_ids = curr_record[1]
                for user in context.args:
                    try:
                        index = new_users.index(user)
                        new_users.pop(index)
                        new_xbox_ids.pop(index)
                    except ValueError:
                        continue
                    
                query = f"UPDATE xbox_status SET names = {create_sql_array(new_users)}, xbox_ids = {create_sql_array(new_xbox_ids)} WHERE id = {group_id}"
                cursor.execute(query)

        update.message.reply_text("Done! The new user(s) have been deleted.")


def list_xbox_status_users(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        listed_status_users = "The users in the status list are:"
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT names, xbox_ids FROM xbox_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                listed_status_users += " No users have been set."
            else:
                for x in range(len(curr_record[0])):
                    listed_status_users += f"\n- {curr_record[0][x]}, {curr_record[1][x]}"  
        update.message.reply_text(listed_status_users)


def xbox_status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        players = []
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT names, xbox_ids FROM xbox_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                update.message.reply_text("No users have been set to show status of.")
            else:
                cursor.execute("SELECT * FROM xbox_credential")
                credentials = cursor.fetchone()
                if not credentials:
                    update.message.reply_text("The administrator first needs to set the credentials using /xbox_credentials_setup")
                    return

                client = XboxApi(credentials[1], credentials[2], {
                    "token_type": credentials[3],
                    "expires_in": credentials[4],
                    "scope": credentials[5],
                    "access_token": credentials[6],
                    "refresh_token": credentials[7],
                    "user_id": credentials[8],
                    "issued": credentials[9] 
                })

                players = asyncio.run(client.get_players(
                    [str(curr_record[1][x]) for x in range(len(curr_record[0]))],
                    [curr_record[0][x] for x in range(len(curr_record[0]))]
                ))
                players = [str(player) for player in players]
                players.sort()
                update.message.reply_text("".join(players))


def add_playstation_status_user(update, context):
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
            cursor.execute('SELECT names, playstation_ids FROM playstation_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                # Create a local copy of our updated list of playstation ids and names.
                new_users = [user[0] for user in users]
                new_playstation_ids = [user[1] for user in users]

                # Build up a query to insert new users as a new record in the table
                query = f"INSERT INTO playstation_status (id, names, playstation_ids) VALUES({group_id}, {create_sql_array(new_users)}, {create_sql_array(new_playstation_ids)})"
                cursor.execute(query)
            else:
                # Create a local copy of our updated list of playstation ids and names.
                new_users = curr_record[0] + [user[0] for user in users]
                new_playstation_ids = curr_record[1] + [user[1] for user in users]

                # Build up a query to insert new users plus any pre-existing ones
                query = f"UPDATE playstation_status SET names = {create_sql_array(new_users)}, playstation_ids = {create_sql_array(new_playstation_ids)} WHERE id = {group_id}"
                cursor.execute(query)

        update.message.reply_text("Done! The new user(s) have been added.")


def del_playstation_status_user(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT names, playstation_ids FROM playstation_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                query = f"INSERT INTO playstation_status (id) VALUES({group_id})"
                cursor.execute(query)
            else:
                new_users = curr_record[0]
                new_playstation_ids = curr_record[1]
                for user in context.args:
                    try:
                        index = new_users.index(user)
                        new_users.pop(index)
                        new_playstation_ids.pop(index)
                    except ValueError:
                        continue
                    
                query = f"UPDATE playstation_status SET names = {create_sql_array(new_users)}, playstation_ids = {create_sql_array(new_playstation_ids)} WHERE id = {group_id}"
                cursor.execute(query)

        update.message.reply_text("Done! The new user(s) have been deleted.")


def list_playstation_status_users(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        listed_status_users = "The users in the status list are:"
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT names, playstation_ids FROM playstation_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                listed_status_users += " No users have been set."
            else:
                for x in range(len(curr_record[0])):
                    listed_status_users += f"\n- {curr_record[0][x]}, {curr_record[1][x]}"  
        update.message.reply_text(listed_status_users)


def playstation_status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        players = []
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT names, playstation_ids FROM playstation_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                update.message.reply_text("No users have been set to show status of.")
            else:
                cursor.execute("SELECT * FROM playstation_credential")
                credentials = cursor.fetchone()
                if not credentials:
                    update.message.reply_text("The administrator first needs to set the credentials using /playstation_credentials_setup")
                    return

                client = PlaystationApi(credentials[1])
                players = client.get_players(
                    [str(curr_record[1][x]) for x in range(len(curr_record[0]))],
                    [curr_record[0][x] for x in range(len(curr_record[0]))]
                )
                players = [str(player) for player in players]
                players.sort()
                update.message.reply_text("".join(players))
