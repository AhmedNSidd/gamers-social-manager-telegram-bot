"""
Script to add a new playstation npsso to the database provided in the DATABASE_URL.
This script assumes that a table with the proper schema already exists at the
database. If this is not the case, look into running
scripts/db/instantiate_tables.py first.

For more information on the obtaining of a Playstation npsso, reference the
DEVELOPMENT.md file at the root of project.
"""
import argparse
import os
import psycopg2
import urllib.parse as urlparse

from psnawp_api import authenticator


url = urlparse.urlparse(os.environ['DATABASE_URL'])

def validate_and_store_npsso(npsso: str):
    # This will raise errors if the npsso is invalid.
    authenticator.Authenticator(npsso) 
    with psycopg2.connect(dbname=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM playstation_credential")
            existing_credentials = cursor.fetchone()
            if existing_credentials and existing_credentials[1] == npsso:
                print("The npsso code provided has already been previously stored and validated!")
            else:
                if existing_credentials:
                    cursor.execute(f"DELETE FROM playstation_credential WHERE id={existing_credentials[0]}")
            
                cursor.execute(f"INSERT INTO playstation_credential (npsso) VALUES('{npsso}')")
                print("Success! The PSN API is now ready to be used.")


def main():
    parser = argparse.ArgumentParser(description="Authenticate the PSN API using an npsso")
    parser.add_argument(
        "--npsso",
        "-n",
        help="The Playstation npsso",
        required=True
    )
    args = parser.parse_args()
    validate_and_store_npsso(args.npsso)


if __name__ == "__main__":
    main()