import os
import psycopg2
import urllib.parse as urlparse

from dotenv import load_dotenv


CREATE_TABLE_IF_NOT_EXISTS = "CREATE TABLE IF NOT EXISTS {}"
DROP_CASCADE = "DROP TABLE {} CASCADE"
SELECT = "SELECT {} FROM {}"
INSERT = "INSERT INTO {} VALUES {}"
SELECT_WHERE = "SELECT {} FROM {} WHERE {}"
SELECT_WHERE_ORDER_BY = "SELECT {} FROM {} WHERE {} ORDER BY {}"
UPDATE_WHERE = "UPDATE {} SET {} WHERE {}"
DELETE_WHERE = "DELETE FROM {} WHERE {}"

class DBConnection:
    instance = None

    def __new__(cls, *args, **kwargs):
        it_id = "__it__"
        it = cls.__dict__.get(it_id, None)
        if it is not None:
            return it
        it = object.__new__(cls)
        setattr(cls, it_id, it)
        it.init(*args, **kwargs)
        return it

    def init(self):
        if not os.getenv("GSM_DB_URL"):
            # Get the path to the directory this file is in
            BASEDIR = os.path.abspath(os.path.dirname(__file__))
            # Connect the path with your '.env' file name
            load_dotenv(os.path.join(BASEDIR, '../../.env'))
            self.URL = urlparse.urlparse(os.getenv("GSM_DB_URL"))
            host = "localhost"
        else:
            self.URL = urlparse.urlparse(os.getenv("GSM_DB_URL"))
            host = self.URL.hostname
    
        self.conn = psycopg2.connect(dbname=self.URL.path[1:],
                                     user=self.URL.username,
                                     password=self.URL.password,
                                     host=host,
                                     port=self.URL.port)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, query):
        self.cursor.execute(query)

    def fetchone(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def fetchall(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
