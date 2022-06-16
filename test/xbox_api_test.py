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

        players = client.get_players(
            [2533274851179327, 2535423896660686, 2533274856229097],
            ["Rickus", "Jas", "Grant"]
        )
                
        players.sort()
        print(players)
