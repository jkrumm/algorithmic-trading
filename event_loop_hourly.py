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


# Map trades from signal
# ------------------------------------------------------------------------------

async def run_map_trade(tickers):
    i = 0
    while i <= len(tickers):
        symbol = tickers[i % len(tickers)]
        yield symbol, map_trade(symbol)
        i += 1
        await asyncio.sleep(1)


def map_trade(ticker):
    signals = transform_cursor(s.find({"ticker": ticker[0], "interval": str(ticker[1])}))
    currencies = transform_cursor_dict(c.find_one({"currency": ticker[0][:-3]}))
    print(currencies)
    btc = transform_cursor_dict(c.find_one({"currency": "BTC"}))
    obj = {
        'id': '',
        'symbol': '',
        'action': '',
        'timeframe': '',
        'date': '',
        'duration': '',
        'price': 0.00,
        'current_price': 0.00,
        'current_profit': 0.00,
        '1d': 0.00,
        '7d': 0.00,
        '30d': 0.00
    }
    if len(signals) > 0 and len(currencies) > 0:
        od = sorted(signals, key=lambda k: k['time'], reverse=True)
        x = od[0]
        obj['id'] = x['ticker'] + x['interval']
        symbol = x['ticker'].replace('XBT', 'BTC')
        if x['ticker'][-3:] == "BTC":
            currencies['price'] = float(currencies['price']) / float(btc['price'])
        obj['symbol'] = symbol
        obj['action'] = x['action']
        obj['timeframe'] = x['interval']
        obj['date'] = x["time"][:19].replace('T', ' ')
        date_now = dateutil.parser.parse(datetime.datetime.now().isoformat()[:19].replace('T', ' '))
        date_signal = dateutil.parser.parse(x["time"][:19].replace('T', ' '))
        obj['duration'] = str(abs(date_now - date_signal))
        obj['price'] = float(x['price'])
        obj['current_price'] = float(currencies['price'])
        val = ((float(currencies['price']) - float(x['price'])) / float(x['price'])) * 100.00
        if x['action'] == "buy":
            obj['current_profit'] = float(val)
        else:
            obj['current_profit'] = float(val * -1)
        obj['1d'] = float(currencies['1d']["price_change_pct"]) * 100
        obj['7d'] = float(currencies['7d']["price_change_pct"]) * 100
        obj['30d'] = float(currencies['30d']["price_change_pct"]) * 100
        print(obj)
        t.update_one({"id": obj['id']}, {"$set": obj})
    return


# Main method
# ------------------------------------------------------------------------------

async def run2():
    async for (symbol, ticker) in run_map_trade(
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
