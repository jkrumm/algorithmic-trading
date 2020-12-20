import asyncio
import json
import requests
from tinydb import TinyDB, Query
from config import NOMICS_KEY

db = TinyDB('db.json')
currencieDb = db.table('currencie')
q = Query()


# Main method
# ------------------------------------------------------------------------------


async def run1():
    while True:
        r = requests.get(
            "https://api.nomics.com/v1/currencies/ticker?key=" + NOMICS_KEY + "&interval=1d,7d,30d&per-page=100&page=1")
        if r.status_code == 200:
            currencieDb.truncate()
            currencieDb.insert_multiple(json.loads(r.content))
            print("Successfully inserted Nomics Currencies")
        else:
            print("Not able to fetch Nomics Currencies : " + str(r.status_code))
        # TODO: Implement alert trigger
        await asyncio.sleep(10)


async def run2():
    while True:
        await asyncio.sleep(10)


# Run async event loop
# ------------------------------------------------------------------------------

loop = asyncio.get_event_loop()
loop.create_task(run1())
# loop.create_task(run2())
loop.run_forever()
