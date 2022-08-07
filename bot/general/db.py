import os
# import urllib.parse as urlparse

from dotenv import load_dotenv
from pymongo import MongoClient


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
        if not os.getenv("GSM_DB_HOSTNAME"):
            # Get the path to the directory this file is in
            BASEDIR = os.path.abspath(os.path.dirname(__file__))
            # Connect the path with your '.env' file name
            load_dotenv(os.path.join(BASEDIR, '../../.env'))
            host = "localhost"
        else:
            host = os.getenv("GSM_DB_HOSTNAME")
        
        url = "mongodb://{}:{}@{}:{}".format(
            os.getenv("GSM_DB_USER_AND_DB"), os.getenv("GSM_DB_PASSWORD"),
            host, os.getenv("GSM_DB_PORT")
        )
        self.db = MongoClient(url)[os.getenv("GSM_DB_USER_AND_DB")]

    def __del__(self):
        self.db.client.close()

    def insert_one(self, collection_name, document):
        collection = self.db[collection_name]
        collection.insert_one(document)

    def insert_many(self, collection_name, documents):
        collection = self.db[collection_name]
        collection.insert_many(documents)

    def find_one(self, collection_name, query=None):
        collection = self.db[collection_name]
        return collection.find_one(query)

    def find(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.find(query)

    def update_one(self, collection_name, filter, update):
        collection = self.db[collection_name]
        collection.update_one(filter, update)

    def count_documents(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.count_documents(query)

    def delete_one(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.delete_one(query)

    def delete_many(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.delete_many(query)

    def drop(self, collection_name):
        collection = self.db[collection_name]
        return collection.drop()

    def list_collection_names(self):
        return self.db.list_collection_names()