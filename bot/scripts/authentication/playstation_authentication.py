"""
Script to add a new playstation npsso to the database provided in the DATABASE_URL.
This script assumes that a table with the proper schema already exists at the
database. If this is not the case, look into running
scripts/db/instantiate_tables.py first.

For more information on the obtaining of a Playstation npsso, reference the
DEVELOPMENT.md file at the root of project.
"""
import argparse
import pathlib
import sys
sys.path.append(pathlib.PurePath(pathlib.Path(__file__).parent.absolute(),
                                 "../..").__str__())

from general.db import DBConnection
from psnawp_api import authenticator
from utils import import_root_dotenv_file

def validate_and_store_npsso(npsso: str):
    # This will raise errors if the npsso is invalid.
    authenticator.Authenticator(npsso)
    # Import the database's credentials from our root .env file
    import_root_dotenv_file()

    credentials = DBConnection().find_one("credentials", {"platform": "psn"})    
    if credentials and credentials["npsso"] == npsso:
        print("The npsso code provided has already been previously stored and "
              "validated!")
    else:
        if credentials:
            DBConnection().update_one(
                "credentials",
                {"platform": "psn"},
                {"$set": {
                    "npsso": npsso
                }}
            )
        else:
            DBConnection().insert_one("credentials",
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
    args = parser.parse_args()
    validate_and_store_npsso(args.npsso)


if __name__ == "__main__":
    main()