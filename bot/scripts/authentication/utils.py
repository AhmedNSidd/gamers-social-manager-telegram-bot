import os

from dotenv import load_dotenv


def import_root_dotenv_file():
    # Import the database's credentials from our root .env file
    curr_file_dir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(curr_file_dir, '../../../.env'))