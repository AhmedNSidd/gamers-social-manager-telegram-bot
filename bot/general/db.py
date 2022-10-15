from pymongo import MongoClient
from pymongo.results import InsertOneResult
from urllib.parse import urlparse, quote_plus


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

    def init(self, db_url: str):
        """
        This intializes the database. Note that there are three separate
        situations in which this class may be initialized under:

        1) The GSM bot is being run in a container under Docker Compose,
        in which case, we can just get the DB url straight from the environment
        variables
        2) This class is being called when we are running a script
        (like in scripts/authentication/) In this case, we need to have
        specified from the script that we are creating running locally so the
        hostname will be localhost, the script also would have needed to import
        environment varibles from the dotenv file in the root of our project
        so we could have access to the db variables we use in this method.
        3) The same script mentioned in 2), is run, but this time for our prod
        database so that 
        """
        self.url = db_url
        self.db = MongoClient(db_url)["gsm"]

    def __del__(self):
        self.db.client.close()

    def insert_one(self, collection_name, document) -> InsertOneResult:
        collection = self.db[collection_name]
        return collection.insert_one(document)

    def insert_many(self, collection_name, documents):
        collection = self.db[collection_name]
        collection.insert_many(documents)

    def find_one(self, collection_name, query=None):
        collection = self.db[collection_name]
        return collection.find_one(query)

    def find(self, collection_name, query):
        collection = self.db[collection_name]
        return list(collection.find(query))

    def update_one(self, collection_name, filter, update, **kwargs):
        collection = self.db[collection_name]
        collection.update_one(filter, update, **kwargs)

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

    @staticmethod
    def authenticate_an_unauthenticated_db_url(unauthenticated_db_url, username, password, is_db_local=False):
        """
        This method is used to convert an unauthenticated database url into a
        database url that has credententials attached to it.
        """
        unauthenticated_parsed_db_url = urlparse(unauthenticated_db_url)

        authenticated_parsed_db_url = unauthenticated_parsed_db_url._replace(
            netloc="{}:{}@{}{}".format(
                username, password,
                ("localhost" if is_db_local else
                 unauthenticated_parsed_db_url.hostname),
                (f":{unauthenticated_parsed_db_url.port}"
                 if unauthenticated_parsed_db_url.port else "")
            )
        )
        encoded_db_url = authenticated_parsed_db_url._replace(
            netloc="{}:{}@{}{}".format(
                quote_plus(authenticated_parsed_db_url.username),
                quote_plus(authenticated_parsed_db_url.password),
                ("localhost" if is_db_local else
                 authenticated_parsed_db_url.hostname),
                (f":{authenticated_parsed_db_url.port}"
                 if authenticated_parsed_db_url.port else "")
            )
        )
        return encoded_db_url.geturl()