import aiohttp
import asyncio

from .apis import XboxLiveApi, PsnApi
from models.user_status import UserStatus
from general.db import DBConnection, SELECT_WHERE


# What do we want to call this class and this file?
# Well we want this class to hold many different APIs and we also want this
# class to initialize all those APIs 

class ApisWrapper:
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

    def init(self):
        ApisWrapper.instance = self
        ApisWrapper.__new__ = lambda _: ApisWrapper.instance
        self.psn_client = PsnApi()
        self.xbox_client = XboxLiveApi()

    async def get_account_id_from_online_id(self, psn_online_id):
        async with aiohttp.ClientSession() as session:
            return await self.psn_client.get_account_id_from_online_id(session,
                                                                 psn_online_id)

    async def get_account_id_from_gamertag(self, xbox_gamertag):
        async with aiohttp.ClientSession() as session:
            return await self.xbox_client.get_account_id_from_gamertag(session,
                                                                 xbox_gamertag)

    async def get_presence_from_apis(self, chat_id):
        """
        This function will return the presence of all the StatusUsers in
        the chat corresponding to the chat_id provided.
        """
        status_users = DBConnection().fetchall(SELECT_WHERE.format(
            "telegramUserID, displayName, xboxGamertag, xboxAccountID, "
            "psnOnlineID, psnAccountID", "StatusUsers",
            f"telegramChatID = {chat_id}"
        ))
        if not status_users:
            return None
        _, _, xbox_gamertags, xbox_account_ids, psn_online_ids, psn_account_ids = zip(*status_users)
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
                    status_users[i][0], status_users[i][1],
                    xbox_status_users_presence[i], psn_status_users_presence[i]
                ))
            return user_statuses