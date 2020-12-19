import datetime
import asyncio
import ccxt.async_support as ccxt
import dateutil.parser
from tinydb import TinyDB, Query

db = TinyDB('db.json')
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
        await asyncio.sleep(3)


def map_trade(ticker):
    b = Query()
    # Get latest entry for symbol and timeframe
    signals = signalDB.search((b.ticker == ticker[0]) & (b.interval == str(ticker[1])))
    # Get pair entry
    symbol_obj = symbolsDb.search(b.symbol == ticker[0])
    if len(symbol_obj) > 0:
        symbol_obj = symbol_obj[0]
    else:
        return
    print("symbol")
    print(ticker)
    print(len(signals))
    print(symbol_obj)
    obj = {
        'symbol': '',
        'action': '',
        'timeframe': '',
        'date': '',
        'duration': '',
        'price': 0.00,
        'current_price': 0.00,
        'current_profit': 0.00
    }
    if len(signals) > 0 and len(symbol_obj) > 0:
        od = sorted(signals, key=lambda k: k['time'], reverse=True)
        x = od[0]
        symbol = x['ticker'].replace('XBT', 'BTC')
        obj['symbol'] = symbol
        obj['action'] = x['action']
        obj['timeframe'] = x['interval']
        obj['date'] = x["time"][:19].replace('T', ' ')
        date_now = dateutil.parser.parse(datetime.datetime.now().isoformat()[:19].replace('T', ' '))
        date_signal = dateutil.parser.parse(x["time"][:19].replace('T', ' '))
        obj['duration'] = str(abs(date_now - date_signal))
        obj['price'] = float(x['price'])
        obj['current_price'] = float(symbol_obj['price'])
        # ((df.iloc[index]['Price'] - df.iloc[index - 1]['Price']) / df.iloc[index - 1]['Price']) * 100.00
        val = ((symbol_obj['price'] - x['price']) / x['price']) * 100.00
        if x['action'] == "buy":
            obj['current_profit'] = float(val)
        else:
            obj['current_profit'] = float(val * -1)
        print("obj")
        print(obj)
        if tradesDb.contains(b.symbol == symbol):
            tradesDb.update(obj, b.symbol == symbol)
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

async def run2():
    async for (symbol, ticker) in run_map_trade(
            [["BTCUSD", 480], ["BTCUSD", 720], ["BTCUSD", 1], ["ETHUSD", 720], ["ETHBTC", 720], ["LINKUSD", 720],
             ["LINKBTC", 720], ["XRPUSD", 720], ["LTCUSD", 720],
             ["EOSUSD", 720], ["ADAUSD", 720]]):
        print(symbol, ticker)


async def run1():
    d = Query()
    symbolsDb.insert({'symbol': 'BTCUSD', 'price': 123})
    async for (symbol, ticker) in poll(
            ['BTC/USD', 'ETH/USD', 'ETH/BTC', 'LINK/USD', 'LINK/BTC', 'XRP/USD', 'LTC/USD', 'EOS/USD', 'ADA/USD']):
        symbol = symbol.replace('/', '')
        if len(symbolsDb.search(d.symbol == symbol)) > 0:
            symbolsDb.update({'symbol': symbol, 'price': ticker["bid"]}, d.symbol == symbol)
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
