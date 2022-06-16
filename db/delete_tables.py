"""
This script will connect to the Heroku Posgresql database and delete all the
existing tables
"""
import os
import psycopg2
import urllib.parse as urlparse


url = urlparse.urlparse(os.environ['DATABASE_URL'])

def delete_tables():
    """
    This function will create the necessary tables for the running of the
    bot if the tables don't already exist in the provided url.

    url: The database URL
    """
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        with conn.cursor() as cursor:
                cursor.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_schema,table_name")
                rows = cursor.fetchall()
                for row in rows:
                    cursor.execute("drop table " + row[1] + " cascade")



if __name__ == "__main__":
    delete_tables()