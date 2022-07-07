"""
This script will connect to the Heroku Posgresql database and create the
tables necessary for the running of the Chaddicts bot if the tables don't
already exist.
"""
import pathlib
import sys
sys.path.append(pathlib.PurePath(pathlib.Path(__file__).parent.absolute(),
                                 "../..").__str__())

from general.db import DBConnection, CREATE_TABLE_IF_NOT_EXISTS, INSERT


def instantiate_tables():
    """
    This function will create the necessary tables for the running of the
    bot if the tables don't already exist in the provided url.
    """
    db = DBConnection()
    db.execute(CREATE_TABLE_IF_NOT_EXISTS.format("StatusUsers (id SERIAL, telegramChatID BIGINT, telegramUserID BIGINT, displayName TEXT, xboxGamertag TEXT, xboxAccountID BIGINT, psnOnlineID TEXT, psnAccountID BIGINT, PRIMARY KEY (id))"))
    db.execute(CREATE_TABLE_IF_NOT_EXISTS.format("Credentials (id INT NOT NULL UNIQUE DEFAULT 1 CHECK (id = 1), xboxClientID TEXT, xboxClientSecret TEXT, xboxTokenType TEXT, xboxExpiresIn INT, xboxScope TEXT, xboxAccessToken TEXT, xboxRefreshToken TEXT, xboxUserID TEXT, xboxIssued TEXT, psnNpsso TEXT)"))
    db.execute(CREATE_TABLE_IF_NOT_EXISTS.format("Notifications (telegramChatID BIGINT PRIMARY KEY, message TEXT, users TEXT[])"))
    db.execute(INSERT.format("Credentials (id)", "(1) ON CONFLICT DO NOTHING"))

if __name__ == "__main__":
    instantiate_tables()