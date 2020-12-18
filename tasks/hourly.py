# -----------------------------------------------------------------------------
import time
from decimal import ROUND_UP

import ccxt

exchange = ccxt.kraken({
    'rateLimit': 1000,
    'enableRateLimit': True,
    # 'verbose': True,
})

msec = 1000
minute = 60 * msec
hold = 30

limit = 500
timeframe = "5m"
interval = exchange.parse_timeframe(timeframe) * 1000

try:
    print(exchange.milliseconds(), 'Fetching candles')
    since = exchange.round_timeframe(timeframe, exchange.milliseconds(), ROUND_UP) - (limit * interval)
    ohlcv = exchange.fetch_ohlcv('ETH/BTC', timeframe, since=since, limit=limit)
    print(exchange.milliseconds(), 'Fetched', len(ohlcv), 'candles')
    first = ohlcv[0][0]
    last = ohlcv[-1][0]
    print('First candle epoch', first, exchange.iso8601(first))
    print('Last candle epoch', last, exchange.iso8601(last))
except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
    print('Got an error', type(error).__name__, error.args, ', retrying in', hold, 'seconds...')
    time.sleep(hold)
