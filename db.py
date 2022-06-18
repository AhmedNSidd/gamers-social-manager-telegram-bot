import os
import psycopg2
import urllib.parse as urlparse


class DBConnection:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(DBConnection)
            return cls.instance
        return cls.instance

    def __init__(self):
        # connect takes url, dbname, user-id, password
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    def connect(self):
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        return psycopg2.connect(dbname=url.path[1:], user=url.username, 
                                password=url.password, host=url.hostname,
                                port=url.port)

    def __del__(self):
        self.cursor.close()
        self.conn.close()