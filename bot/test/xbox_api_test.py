"""
This is a test script that uses the Xbox API defined in the external_handlers/
folder and it prints the statuses for the given Xbox Live Gamertags how they
would be formatted in a telegram chat.
"""
import asyncio
import pathlib
import sys
import time
sys.path.append(pathlib.PurePath(pathlib.Path(__file__).parent.absolute(),
                                 "..").__str__())
from external_handlers.apis import XboxLiveApi


def main():
    gamertags = ["JeSuisAhmedN", "Cell520", "JassyLamb", "WizardBinkie760",
                 "WARHEAD1996", "Lynx", "Canadian David7", "Tam not Sam"]
    account_ids = [2535442671459226, 2533274856229097, 2535423896660686,
                   2535445802251685, 2533274841295769, 2645864781080579,
                   2533274851179327, 2533274861060066]
    client = XboxLiveApi()
    st = time.time()
    presences = asyncio.run(client.get_players_presences(account_ids, gamertags))
    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')
    # for presence in presences:
    #     print(presence)


if __name__ == "__main__":
    main()
