import asyncio
import json
import time

import requests
from config import NOMICS_KEY, MONGO_URI
import pymongo

m = pymongo.MongoClient(MONGO_URI)
c = m['<dbname>'].currencies


# Main method
# ------------------------------------------------------------------------------


async def run1():
    while True:
        r = requests.get(
            "https://api.nomics.com/v1/currencies/ticker?key=" + NOMICS_KEY + "&interval=1d,7d,30d&per-page=100&page=1")
        if r.status_code == 200:
            data = json.loads(r.content)
            if c.estimated_document_count() > 0:
                for d in data:
                    c.update_one({"id": d['id']}, {"$set": d})
                print("Updated")
            else:
                c.insert_many(data)
            print("Successfully inserted Nomics Currencies")
        else:
            print("Not able to fetch Nomics Currencies : " + str(r.status_code))
        await asyncio.sleep(60)


async def run2():
    while True:
        await asyncio.sleep(10)


# Run async event loop
# ------------------------------------------------------------------------------

loop = asyncio.get_event_loop()
loop.create_task(run1())
# loop.create_task(run2())
loop.run_forever()
time.sleep(5)
