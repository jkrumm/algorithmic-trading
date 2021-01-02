import datetime
import asyncio
import dateutil.parser
import pymongo

from config import MONGO_URI
from utils.helper import transform_cursor, transform_cursor_dict

m = pymongo.MongoClient(MONGO_URI)
s = m['<dbname>'].signals
t = m['<dbname>'].trades
c = m['<dbname>'].currencies


# Map profit from signal
# ------------------------------------------------------------------------------

async def run_map_profit(tickers):
    i = 0
    while i <= len(tickers):
        symbol = tickers[i % len(tickers)]
        yield symbol, map_profit(symbol)
        i += 1
        await asyncio.sleep(1)


def map_profit(ticker):
    signals = s.find({"ticker": ticker[0], "interval": str(ticker[1])})
    currencies = transform_cursor_dict(c.find_one({"currency": ticker[0][:-3]}))
    print(ticker[0], ticker[1])
    btc = transform_cursor_dict(c.find_one({"currency": "BTC"}))
    if signals.count() > 0 and len(currencies) > 0:
        od = sorted(signals, key=lambda k: k['time'], reverse=True)
        if od[0]['ticker'][-3:] == "BTC":
            currencies['price'] = float(currencies['price']) / float(btc['price'])
        print(od[0])
        profit = ((float(currencies['price']) - float(od[0]['price'])) / float(od[0]['price'])) * 100
        if od[0]['action'] == "sell":
            profit = profit * -1
        s.update_one({'_id': od[0]['_id']}, {"$set": {"profit": profit}})
        for i in range(5):
            if i > 0:
                profit = ((float(od[i - 1]['price']) - float(od[i]['price'])) / float(od[i]['price'])) * 100
                if od[i]['action'] == "buy":
                    print("buy", od[i]['price'], od[i - 1]['price'], profit)
                else:
                    profit = profit * -1
                    print("sell", od[i]['price'], od[i - 1]['price'], profit)
                s.update_one({'_id': od[i]['_id']}, {"$set": {"profit": profit}})
    return


# Main method
# ------------------------------------------------------------------------------

async def run2():
    async for (symbol, ticker) in run_map_profit(
            [["BTCUSD", 480], ["BTCUSD", 720], ["BTCUSD", 1], ["ETHUSD", 720], ["ETHBTC", 720], ["LINKUSD", 720],
             ["LINKBTC", 720], ["XRPUSD", 720], ["LTCUSD", 720], ["EOSUSD", 720], ["ADAUSD", 720]]):
        print(symbol, ticker)


async def run1():
    while True:
        await asyncio.sleep(10)


# Run async event loop
# ------------------------------------------------------------------------------

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(run2())
    loop.run_until_complete(asyncio.wait([run2()]))


main()
