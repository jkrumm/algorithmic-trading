import datetime
import asyncio
import ccxt.async_support as ccxt
import dateutil.parser
from tinydb import TinyDB, Query

db = TinyDB('../db.json')
signalDB = db.table('signal')
symbolsDb = db.table('symbols')
tradesDb = db.table('trades')
q = Query()

kraken = ccxt.kraken()


# Map trades from signal
# ------------------------------------------------------------------------------

async def run_map_trade(tickers):
    i = 0
    while True:
        symbol = tickers[i % len(tickers)]
        yield symbol, map_trade(symbol)
        i += 1
        await asyncio.sleep(5)


def map_trade(ticker):
    # Get latest entry for symbol and timeframe
    signals = signalDB.search((q.ticker == ticker[0]) & (q.interval == str(ticker[1])))
    obj = {
        'symbol': '',
        'action': '',
        'timeframe': '',
        'date': '',
        'duration': '',
        'price': ''
    }
    if len(signals) > 0:
        od = sorted(signals, key=lambda k: k['time'], reverse=True)
        x = od[0]
        symbol = x['ticker'] if x['ticker'] != 'XBTUSD' else 'BTCUSD'
        obj['symbol'] = symbol
        obj['action'] = x['action']
        obj['timeframe'] = x['interval']
        obj['date'] = x["time"][:19].replace('T', ' ')
        date_now = dateutil.parser.parse(datetime.datetime.now().isoformat()[:19].replace('T', ' '))
        date_signal = dateutil.parser.parse(x["time"][:19].replace('T', ' '))
        obj['duration'] = str(abs(date_now - date_signal))
        obj['price'] = x['price']
        if tradesDb.contains(q.symbol == symbol):
            tradesDb.update(obj, q.symbol == symbol)
        else:
            tradesDb.insert(obj)
    return


# Ticker for all pairs
# ------------------------------------------------------------------------------

async def poll(tickers):
    i = 0
    while True:
        symbol = tickers[i % len(tickers)]
        yield symbol, await kraken.fetch_ticker(symbol)
        i += 1
        await asyncio.sleep(kraken.rateLimit / 1000)


# Main method
# ------------------------------------------------------------------------------

async def run1():
    async for (symbol, ticker) in run_map_trade(
            [["BTCUSD", 8], ["BTCUSD", 12], ["BTCUSD", 1], ["ETHUSD", 12], ["ETHBTC", 12], ["LINKUSD", 12],
             ["LINKBTC", 12], ["XRPUSD", 12], ["LTCUSD", 12],
             ["EOSUSD", 12], ["ADAUSD", 12]]):
        print(symbol, ticker)


async def run2():
    symbolsDb.insert({'symbol': 'BTCUSD', 'price': 123})
    async for (symbol, ticker) in poll(
            ['BTC/USD', 'ETH/USD', 'ETH/BTC', 'LINK/USD', 'LINK/BTC', 'XRP/USD', 'LTC/USD', 'EOS/USD', 'ADA/USD']):
        symbol = symbol.replace('/', '')
        if symbolsDb.contains(q.symbol == symbol):
            symbolsDb.update({'symbol': symbol, 'price': ticker["bid"]}, q.symbol == symbol)
        else:
            symbolsDb.insert({'symbol': symbol, 'price': ticker["bid"]})
        print(symbol, ticker["bid"])
        print(symbolsDb.all())


# Run async event loop
# ------------------------------------------------------------------------------

# asyncio.get_event_loop().run_until_complete(main())

loop = asyncio.get_event_loop()
loop.create_task(run1())
loop.create_task(run2())
loop.run_forever()
