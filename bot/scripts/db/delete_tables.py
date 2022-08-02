"""
This script will connect to the Heroku Posgresql database for the bot and
delete all the existing tables.
"""
import pathlib
import sys
sys.path.append(pathlib.PurePath(pathlib.Path(__file__).parent.absolute(),
                                 "../..").__str__())
                                
from general.db import DBConnection, DROP_CASCADE, SELECT_WHERE_ORDER_BY


def delete_tables():
    """
    This function will create the necessary tables for the running of the
    bot if the tables don't already exist in the provided url.
    """
    db = DBConnection()
    response = input(f"Warning! This will delete ALL the tables and the data\nwithin for the database stored in the DATABASE_URL environment variable which is:\n\n{db.URL.geturl()}\n\nEnter y to confirm this or any other character to cancel: ")
    if response == "y":
        rows = db.fetchall(SELECT_WHERE_ORDER_BY.format(
            "table_schema,table_name", "information_schema.tables",
            "table_schema = 'public'", "table_schema,table_name"))
        if not rows:
            print("No tables exist!")
            return
        for table in rows:
            print(f"Executed {DROP_CASCADE.format(f'{table[1]}')}")
            db.execute(DROP_CASCADE.format(f"{table[1]}"))
        rows = db.fetchall(SELECT_WHERE_ORDER_BY.format(
            "table_schema,table_name", "information_schema.tables",
            "table_schema = 'public'", "table_schema,table_name"))
        print("Tables have been deleted.")
    else:
        print("y was not entered. Stopping the script.")



if __name__ == "__main__":
    delete_tables()