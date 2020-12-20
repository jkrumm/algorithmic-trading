import datetime
import asyncio
import dateutil.parser
from tinydb import TinyDB, Query

db = TinyDB('db.json')
signalDB = db.table('signal')
currencieDb = db.table('currencie')
tradesDb = db.table('trades')
q = Query()


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
    # tradesDb.truncate()
    # Get latest entry for symbol and timeframe
    signals = signalDB.search((q.ticker == ticker[0]) & (q.interval == str(ticker[1])))
    # Get pair entry
    c = currencieDb.search(q.currency == ticker[0][:-3])
    btc = currencieDb.search(q.currency == "BTC")[0]
    if len(c) > 0:
        c = c[0]
    else:
        print("Didn't find a currency in hourly task 1")
        # TODO: Implement alert trigger
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
    if len(signals) > 0 and len(c) > 0:
        od = sorted(signals, key=lambda k: k['time'], reverse=True)
        x = od[0]
        obj['id'] = x['ticker'] + x['interval']
        symbol = x['ticker'].replace('XBT', 'BTC')
        if x['ticker'][-3:] == "BTC":
            c['price'] = float(c['price']) / float(btc['price'])
        obj['symbol'] = symbol
        obj['action'] = x['action']
        obj['timeframe'] = x['interval']
        obj['date'] = x["time"][:19].replace('T', ' ')
        date_now = dateutil.parser.parse(datetime.datetime.now().isoformat()[:19].replace('T', ' '))
        date_signal = dateutil.parser.parse(x["time"][:19].replace('T', ' '))
        obj['duration'] = str(abs(date_now - date_signal))
        obj['price'] = float(x['price'])
        obj['current_price'] = float(c['price'])
        val = ((float(c['price']) - x['price']) / x['price']) * 100.00
        if x['action'] == "buy":
            obj['current_profit'] = float(val)
        else:
            obj['current_profit'] = float(val * -1)
        obj['1d'] = float(c['1d']["price_change_pct"]) * 100
        obj['7d'] = float(c['7d']["price_change_pct"]) * 100
        obj['30d'] = float(c['30d']["price_change_pct"]) * 100
        print(obj)
        if len(tradesDb.search(q.id == obj['id'])) > 0:
            tradesDb.update(obj, q.id == obj['id'])
        else:
            tradesDb.insert(obj)
    return


# Main method
# ------------------------------------------------------------------------------

async def run2():
    async for (symbol, ticker) in run_map_trade(
            [["BTCUSD", 480], ["BTCUSD", 720], ["BTCUSD", 1], ["ETHUSD", 720], ["ETHBTC", 720], ["LINKUSD", 720],
             ["LINKBTC", 720], ["XRPUSD", 720], ["LTCUSD", 720],
             ["EOSUSD", 720], ["ADAUSD", 720]]):
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
