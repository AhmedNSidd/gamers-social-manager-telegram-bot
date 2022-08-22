import aiohttp
import asyncio

from .apis import XboxLiveApi, PsnApi
from general.db import DBConnection
from models.user_status import UserStatus


# What do we want to call this class and this file?
# Well we want this class to hold many different APIs and we also want this
# class to initialize all those APIs 

class ApisWrapper:

    def __new__(cls, *args, **kwargs):
        it_id = "__it__"
        it = cls.__dict__.get(it_id, None)
        if it is not None:
            return it
        it = object.__new__(cls)
        setattr(cls, it_id, it)
        it.init(*args, **kwargs)
        return it

    def init(self):
        self.psn_client = PsnApi()
        self.xbox_client = XboxLiveApi()
    
    def _group_account_ids_and_gaming_usernames(self, status_users):
        """
        This helper function takes in a list of dictionary of status users
        and returns their account ids and online ids grouped up into individual
        lists.
        """
        xbox_gamertags, xbox_account_ids, psn_online_ids, psn_account_ids = [], [], [], []
        for status_user in status_users:
            xbox_gamertags.append(status_user.get("xbox_gamertag"))
            xbox_account_ids.append(status_user.get("xbox_account_id"))
            psn_online_ids.append(status_user.get("psn_online_id"))
            psn_account_ids.append(status_user.get("psn_account_id"))
        
        return (xbox_gamertags, xbox_account_ids, psn_online_ids, psn_account_ids)

    async def get_account_id_from_online_id(self, psn_online_id):
        async with aiohttp.ClientSession() as session:
            return await self.psn_client.get_account_id_from_online_id(session,
                                                                 psn_online_id)

    async def get_account_id_from_gamertag(self, xbox_gamertag):
        async with aiohttp.ClientSession() as session:
            return await self.xbox_client.get_account_id_from_gamertag(
                session, xbox_gamertag
            )

    async def get_presence_from_apis(self, chat_id):
        """
        This function will return the presence of all the StatusUsers in
        the chat corresponding to the chat_id provided.
        """
        status_users = list(DBConnection().find(
            "statususers", {"chat_id": chat_id}
        ))
        if not status_users:
            return None
        xbox_gamertags, xbox_account_ids, psn_online_ids, psn_account_ids = self._group_account_ids_and_gaming_usernames(status_users)
        async with aiohttp.ClientSession() as session:
            xbox_presence_task = asyncio.create_task(
                self.xbox_client.get_players_presences(
                    session, xbox_account_ids, xbox_gamertags
                )
            )
            psn_presence_task = asyncio.create_task(
                self.psn_client.get_players_presences(
                    session, psn_account_ids, psn_online_ids
                )
            )
            xbox_status_users_presence = await xbox_presence_task
            psn_status_users_presence = await psn_presence_task
            user_statuses = []
            for i in range(len(xbox_status_users_presence)):
                user_statuses.append(UserStatus(
                    status_users[i]["user_id"], status_users[i]["display_name"],
                    xbox_status_users_presence[i], psn_status_users_presence[i]
                ))
            return user_statuses
