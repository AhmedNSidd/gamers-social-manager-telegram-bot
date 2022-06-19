"""
This is a test script that uses the Playstation API defined in the
external_handlers/ folder and it prints the statuses for the given PSN Online
IDs how they would be formatted in a telegram chat.
"""
import os
import psycopg2
import urllib.parse as urlparse

from external_handlers.playstation_api import PlaystationApi


url = urlparse.urlparse(os.environ['DATABASE_URL'])

with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM playstation_credential")
        credentials = cursor.fetchone()

        client = PlaystationApi(credentials[1])

        players = client.get_players(["PSNOnlineID1", "PSNOnlineID2",
                                     "PSNOnlineID3"])
                
        players.sort()
        print("".join(players))
