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
import pathlib
import sys
sys.path.append(pathlib.PurePath(pathlib.Path(__file__).parent.absolute(),
                                 "../..").__str__())

from general.utils import import_root_dotenv_file
from general.db import DBConnection
from psnawp_api.core.authenticator import Authenticator as PSNAWPAuthenticator


def validate_and_store_npsso(db: DBConnection, npsso: str):
    # This will raise errors if the npsso is invalid.
    PSNAWPAuthenticator(npsso)

    credentials = db.find_one("credentials", {"platform": "psn"})    
    if credentials and credentials["npsso"] == npsso:
        print("The npsso code provided has already been previously stored and "
              "validated!")
    else:
        if credentials:
            db.update_one(
                "credentials",
                {"platform": "psn"},
                {"$set": {
                    "npsso": npsso
                }}
            )
        else:
            db.insert_one("credentials",
                {
                    "platform": "psn",
                    "npsso": npsso
                }
            )
        print("Success! The PSN API is now ready to be used.")


def main():
    parser = argparse.ArgumentParser(description="Authenticate the PSN API using an npsso")
    parser.add_argument(
        "--npsso",
        "-n",
        help="The Playstation npsso",
        required=True
    )
    parser.add_argument(
        "--localdb",
        help="Indicates whether the database is running on localhost or not",
        action="store_true"
    )
    args = parser.parse_args()
    if args.localdb:
        import_root_dotenv_file()
        
    # Set up the database singleton object
    db = DBConnection(DBConnection.authenticate_an_unauthenticated_db_url(
        os.getenv("GSM_DB_URL_WITHOUT_USERNAME_AND_PASSWORD"),
        os.getenv("GSM_DB_USERNAME"), os.getenv("GSM_DB_PASSWORD"),
        is_db_local=args.localdb
    ))

    validate_and_store_npsso(db, args.npsso)
    db.__del__()


if __name__ == "__main__":
    main()