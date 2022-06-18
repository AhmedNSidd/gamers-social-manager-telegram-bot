import asyncio
import os
import psycopg2
import urllib.parse as urlparse

from general.utils import create_sql_array
from external_handlers.xbox_api import XboxApi
from external_handlers.playstation_api import PlaystationApi


url = urlparse.urlparse(os.environ['DATABASE_URL'])

def add_xbox_status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            gamertags_to_add = set([])
            for gamertag in update['message']['text'][update['message']['text'].find(" "):].split(','):
                gamertags_to_add.add(gamertag.strip())
            cursor.execute('SELECT gamertags FROM xbox_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record:
                # Build up a query to insert new users as a new record in the table
                query = f"INSERT INTO xbox_status (id, gamertags) VALUES({group_id}, {create_sql_array(list(gamertags_to_add))})"
                cursor.execute(query)
            else:
                # Add in all the preexisting gamertags in the table if they exist
                if curr_record[0]:
                    existing_gamertags = set(curr_record[0])
                    gamertags_to_add = list(existing_gamertags.union(gamertags_to_add))

                # Build up a query to insert new users plus any pre-existing ones
                query = f"UPDATE xbox_status SET gamertags = {create_sql_array(list(gamertags_to_add))} WHERE id = {group_id}"
                cursor.execute(query)

    update.message.reply_text("Done! The new user(s) have been added.")


def del_xbox_status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            gamertags_to_delete = set([])
            for gamertag in update['message']['text'][update['message']['text'].find(" "):].split(','):
                gamertags_to_delete.add(gamertag.strip())
            cursor.execute('SELECT gamertags FROM xbox_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record:
                query = f"INSERT INTO xbox_status (id) VALUES({group_id})"
                cursor.execute(query)
            elif not curr_record[0]:
                update.message.reply_text("No users exists to delete.")
                return
            else:
                gamertags_to_update = curr_record[0]
                for gamertag_to_delete in gamertags_to_delete:
                    try:
                        gamertags_to_update.remove(gamertag_to_delete)
                    except ValueError:
                        # TODO: This fails silently but it might be worth letting the user know that some gamertags were not deleted.
                        continue
                    
                query = f"UPDATE xbox_status SET gamertags = {create_sql_array(gamertags_to_update)} WHERE id = {group_id}"
                cursor.execute(query)

        update.message.reply_text("Done! The provided user(s) have been deleted.")


def list_xbox_status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        listed_status_users = "The users in the status list are:"
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT gamertags FROM xbox_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                listed_status_users += " No users have been set."
            else:
                for x in range(len(curr_record[0])):
                    listed_status_users += f"\n- {curr_record[0][x]}"
        update.message.reply_text(listed_status_users)


def xbox_status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        players = []
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT gamertags FROM xbox_status WHERE id = {}'.format(group_id))
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

                players = asyncio.run(client.get_players(curr_record[0]))
                players = [str(player) for player in players]
                players.sort()
                update.message.reply_text("".join(players))


def add_playstation_status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            psn_online_ids_to_add = set([])
            for psn_online_id in update['message']['text'][update['message']['text'].find(" "):].split(','):
                psn_online_ids_to_add.add(psn_online_id.strip())
            cursor.execute('SELECT psn_online_ids FROM playstation_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record:
                # Build up a query to insert new users as a new record in the table
                query = f"INSERT INTO playstation_status (id, psn_online_ids) VALUES({group_id}, {create_sql_array(list(psn_online_ids_to_add))})"
                cursor.execute(query)
            else:
                # Add in all the preexisting psn online ids in the table if they exist
                if curr_record[0]:
                    existing_psn_online_ids = set(curr_record[0])
                    psn_online_ids_to_add = existing_psn_online_ids.union(psn_online_ids_to_add)
                # Build up a query to insert new users plus any pre-existing ones
                query = f"UPDATE playstation_status SET psn_online_ids = {create_sql_array(list(psn_online_ids_to_add))} WHERE id = {group_id}"
                cursor.execute(query)

        update.message.reply_text("Done! The new user(s) have been added.")


def del_playstation_status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        if not context.args:
            update.message.reply_text("You need to provide arguments to this command! See /help")
            return
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            psn_online_ids_to_delete = set([])
            for psn_online_id in update['message']['text'][update['message']['text'].find(" "):].split(','):
                psn_online_ids_to_delete.add(psn_online_id.strip())
            cursor.execute('SELECT psn_online_ids FROM playstation_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                if not curr_record:
                    query = f"INSERT INTO playstation_status (id) VALUES({group_id})"
                    cursor.execute(query)
                update.message.reply_text("No users exists to delete.")
            else:
                psn_online_ids_to_update = curr_record[0]
                for online_id_to_delete in psn_online_ids_to_delete:
                    try:
                        psn_online_ids_to_update.remove(online_id_to_delete)
                    except ValueError:
                        # TODO: This fails silently but it might be worth letting the user know that some gamertags were not deleted.
                        continue
                    
                query = f"UPDATE playstation_status SET psn_online_ids = {create_sql_array(psn_online_ids_to_update)} WHERE id = {group_id}"
                cursor.execute(query)
                update.message.reply_text("Done! The provided user(s) have been deleted.")


def list_playstation_status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        listed_status_users = "The users in the status list are:"
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT psn_online_ids FROM playstation_status WHERE id = {}'.format(group_id))
            curr_record = cursor.fetchone()
            if not curr_record or not curr_record[0]:
                listed_status_users += " No users have been set."
            else:
                for psn_online_id in curr_record[0]:
                    listed_status_users += f"\n- {psn_online_id}"
        update.message.reply_text(listed_status_users)


def playstation_status(update, context):
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        players = []
        group_id = str(update.effective_chat.id)
        with conn.cursor() as cursor:
            cursor.execute('SELECT psn_online_ids FROM playstation_status WHERE id = {}'.format(group_id))
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
                players = client.get_players(curr_record[0])
                players = [str(player) for player in players]
                players.sort()
                update.message.reply_text("".join(players))
