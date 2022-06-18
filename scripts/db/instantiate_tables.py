"""
This script will connect to the Heroku Posgresql database and create the
tables necessary for the running of the Chaddicts bot if the tables don't
already exist.
"""
import os
import psycopg2
import urllib.parse as urlparse


url = urlparse.urlparse(os.environ['DATABASE_URL'])

def instantiate_tables():
    """
    This function will create the necessary tables for the running of the
    bot if the tables don't already exist in the provided url.

    url: The database URL
    """
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS xbox_status (id BIGINT PRIMARY KEY, gamertags TEXT[])")
            cursor.execute("CREATE TABLE IF NOT EXISTS playstation_status (id BIGINT PRIMARY KEY, psn_online_ids TEXT[])")
            cursor.execute("CREATE TABLE IF NOT EXISTS xbox_credential (id SERIAL PRIMARY KEY, client_id TEXT, client_secret TEXT, token_type TEXT, expires_in INT, scope TEXT, access_token TEXT, refresh_token TEXT, user_id TEXT, issued TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS playstation_credential (id SERIAL PRIMARY KEY, npsso TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS notifications (id BIGINT PRIMARY KEY, message TEXT, users TEXT[])")
