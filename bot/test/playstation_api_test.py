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
from external_handlers.apis import PsnApi

async def main():
    online_ids = ["JeSuisAhmedN", "NimbleSlothSwims", "GPock8",
                  "Powerless-Rabbit", "GraveBias", "silv3rstr3ak",
                  "Tam_not_Sam", "JassyLamb", "Saleh1_3"]
    account_ids = [4654411991183578388, 8935577953138603589, 6636691886801663034,
                   876334464644026317, 8394004071196607081, 6448195725827146162,
                   529626866024451776, 7425961013592611393, 2335563073228162671]
    client = PsnApi()
    st = time.time()
    async with aiohttp.ClientSession() as session:
        presences = await client.get_players_presences(session, account_ids, online_ids)
    et = time.time()
    elapsed_time = et - st

    print('Runtime time:', elapsed_time, 'seconds')
    for presence in presences:
        print(presence)

if __name__ == "__main__":
    asyncio.run(main())
