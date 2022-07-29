"""
This is a test script that uses the Playstation API defined in the
external_handlers/ folder and it prints the statuses for the given PSN Online
IDs how they would be formatted in a telegram chat.
"""
import aiohttp
import asyncio
import pathlib
import sys
import time

sys.path.append(pathlib.PurePath(pathlib.Path(__file__).parent.absolute(),
                                 "..").__str__())
from external_handlers.apis import PsnApi, XboxLiveApi

async def main():
    online_ids = ["JeSuisAhmedN", "NimbleSlothSwims", "GPock8",
                  "Powerless-Rabbit", "GraveBias", "silv3rstr3ak",
                  "Tam_not_Sam", "JassyLamb", "Saleh1_3"]
    psn_account_ids = [4654411991183578388, 8935577953138603589, 6636691886801663034,
                       876334464644026317, 8394004071196607081, 6448195725827146162,
                       529626866024451776, 7425961013592611393, 2335563073228162671]
    gamertags = ["JeSuisAhmedN", "Cell520", "JassyLamb", "WizardBinkie760",
                 "WARHEAD1996", "Lynx", "Canadian David7", "Tam not Sam"]
    xbox_account_ids = [2535442671459226, 2533274856229097, 2535423896660686,
                        2535445802251685, 2533274841295769, 2645864781080579,
                        2533274851179327, 2533274861060066]
    async with aiohttp.ClientSession() as session:
        xbox_client = XboxLiveApi()
        psn_client = PsnApi()
        st = time.time()
        for x in range(10):
            task1 = asyncio.create_task(xbox_client.get_players_presences(session, xbox_account_ids, gamertags))
            task2 = asyncio.create_task(psn_client.get_players_presences(session, psn_account_ids, online_ids))
            await task1
            await task2
        et = time.time()
        elapsed_time = et - st
        print('Execution time:', elapsed_time/10, 'seconds')
    # for presence in presences:
    #     print(presence)

if __name__ == "__main__":
    asyncio.run(main())

