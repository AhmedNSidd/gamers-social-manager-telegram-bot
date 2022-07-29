import os
import psycopg2
import urllib.parse as urlparse


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
    URL = urlparse.urlparse(os.environ['DATABASE_URL'])

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
        self.conn = psycopg2.connect(dbname=DBConnection.URL.path[1:],
                                     user=DBConnection.URL.username,
                                     password=DBConnection.URL.password,
                                     host=DBConnection.URL.hostname,
                                     port=DBConnection.URL.port)
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
