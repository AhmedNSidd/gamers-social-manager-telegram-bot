import os

from pymongo import MongoClient
from urllib.parse import urlparse, quote_plus


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

    def init(self, local=False):
        db_username = os.getenv("GSM_DB_USERNAME")
        db_password = os.getenv("GSM_DB_PASSWORD")
        unauthenticated_parsed_db_url = urlparse(
            os.getenv("GSM_DB_URL_WITHOUT_USERNAME_AND_PASSWORD")
        )
        authenticated_parsed_db_url = unauthenticated_parsed_db_url._replace(
            netloc="{}:{}@{}:{}".format(
                db_username, db_password,
                "localhost" if local else unauthenticated_parsed_db_url.hostname,
                unauthenticated_parsed_db_url.port
            )
        )
        encoded_db_url = authenticated_parsed_db_url._replace(
            netloc="{}:{}@{}:{}".format(
                quote_plus(authenticated_parsed_db_url.username),
                quote_plus(authenticated_parsed_db_url.password),
                "localhost" if local else authenticated_parsed_db_url.hostname,
                authenticated_parsed_db_url.port
            )
        )

        self.db = MongoClient(encoded_db_url.geturl())["gsm"]

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