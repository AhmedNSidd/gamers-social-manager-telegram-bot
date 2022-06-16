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

        players = client.get_players(
            [8935577953138603589, 2335563073228162671, 876334464644026317],
            ["Karlissa", "Raf", "David"]
        )
                
        players.sort()
        print(players)
