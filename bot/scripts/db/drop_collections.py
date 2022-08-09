"""
This script will connect to the Mongodb for the bot and delete all collections
except for the credentials table.
"""
import pathlib
import sys
sys.path.append(pathlib.PurePath(pathlib.Path(__file__).parent.absolute(),
                                 "../..").__str__())
                                
from general.db import DBConnection


def delete_tables():
    """
    This function will create the necessary tables for the running of the
    bot if the tables don't already exist in the provided url.
    """
    response = input(f"Warning! This will delete ALL the tables and the data\nwithin for the database stored in the DATABASE_URL environment variable which is:\n\n{db.URL.geturl()}\n\nEnter y to confirm this or any other character to cancel: ")
    if response == "y":
        collection_names = DBConnection().list_collection_names()
        if not collection_names:
            print("No tables exist!")
            return
        for collection_name in collection_names:
            if collection_name == "credentials":
                continue
            print(f"Dropped the {collection_name} collection")
            DBConnection().drop(collection_name)
    
        print("Collections have been dropped.")
    else:
        print("y was not entered. Stopping the script.")


if __name__ == "__main__":
    delete_tables()