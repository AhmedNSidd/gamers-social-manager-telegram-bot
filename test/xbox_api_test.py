"""
This is a test script that uses the Xbox API defined in the external_handlers/
folder and it prints the statuses for the given Xbox Live Gamertags how they
would be formatted in a telegram chat.
"""
import os
import psycopg2
import urllib.parse as urlparse

from external_handlers.xbox_api import XboxApi


url = urlparse.urlparse(os.environ['DATABASE_URL'])

with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM xbox_credentials")
        credentials = cursor.fetchone()

        client = XboxApi(credentials[1], credentials[2], {
            "token_type": credentials[3],
            "expires_in": credentials[4],
            "scope": credentials[5],
            "access_token": credentials[6],
            "refresh_token": credentials[7],
            "user_id": credentials[8],
            "issued": credentials[9] 
        })

        players = client.get_players(["XboxGamertag1", "XboxGamertag2",
                                     "XboxGamertag3"])
                
        players.sort()
        print("".join(players))
