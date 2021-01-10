import time

start_time = time.time()
from datetime import datetime
import asyncio
import dateutil.parser as parser
import pymongo
import pandas as pd
import json

from config import MONGO_URI
from utils.helper import transform_cursor, transform_cursor_dict

m = pymongo.MongoClient(MONGO_URI)
s = m['<dbname>'].signals
t = m['<dbname>'].trades
tl = m['<dbname>'].trades_latest
tb = m['<dbname>'].trades_best
c = m['<dbname>'].currencies
p = m['<dbname>'].performance

results = []


# s.delete_many({"ticker": "BTCUSD", "interval": "720"})

# Map trades from signal
# ------------------------------------------------------------------------------

async def run_map_trade(tickers):
    i = 0
    while i <= len(tickers):
        symbol = tickers[i % len(tickers)]
        yield symbol, map_trade(symbol)
        i += 1
        await asyncio.sleep(0)


def map_trade(ticker):
    signals = transform_cursor(s.find({"ticker": ticker[0], "interval": str(ticker[1])}))
    currencies = transform_cursor_dict(c.find_one({"currency": ticker[0][:-3]}))
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
        date_now = parser.parse(datetime.now().isoformat()[:19].replace('T', ' '))
        date_signal = parser.parse(x["time"][:19].replace('T', ' '))
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


async def run_map_performance(tickers, results=results):
    i = 0
    while i <= len(tickers):
        symbol = tickers[i % len(tickers)]
        yield symbol, map_performance(symbol)
        i += 1
        await asyncio.sleep(0)


def map_performance(ticker, results=results):
    date_now = parser.parse(datetime.now().isoformat()[:19].replace('T', ' '))

    # for b in ticker:
    ticker_val = str(ticker[0])
    timeframe_val = ticker[1]
    signals = transform_cursor(s.find({"ticker": ticker_val, "interval": str(timeframe_val)}))
    currencies = c.find_one({"currency": ticker_val[:-3]})
    signals_ordered = sorted(signals, key=lambda k: k['time'])
    for x in [365, 730, 1825, 0]:
        s_pd = pd.DataFrame.from_dict(signals_ordered)
        results.append(backtest(s_pd, currencies, ticker_val, timeframe_val, "buy_sell", x, date_now))
        results.append(
            backtest(s_pd[s_pd.action == "buy"], currencies, ticker_val, timeframe_val, "buy", x, date_now))
        results.append(
            backtest(s_pd[s_pd.action == "sell"], currencies, ticker_val, timeframe_val, "sell", x, date_now))


def backtest(df, cur, a, b, c, timespan, date_now):
    print(a + '-' + str(b) + '-' + c + '-' + str(timespan) + " // " + str(df.ticker.count()))
    for index, row in df.iterrows():
        if timespan != 0 and abs(date_now - parser.parse(row["time"][:19].replace('T', ' '))).days > timespan:
            df.drop(index, inplace=True)
    df = df.reset_index(drop=True)
    first = df.iloc[0]
    net_profit = 0.0
    gross_profit = 0.0
    gross_lost = 0.0
    buy_hold = float("{:.2f}".format(((float(cur['price']) - float(first['price'])) / float(first['price'])) * 100.0))
    total_trades = df.count().ticker
    won_trades = 0
    lost_trades = 0
    largest_win = 0.0
    largest_lost = 0.0

    date_signal = parser.parse(df.iloc[0]["time"][:19].replace('T', ' '))
    first_signal = date_signal
    duration = abs(date_now - date_signal)
    duration_days = duration.days

    for index, row in df.iterrows():
        net_profit = net_profit + row['profit']
        if row['profit'] > 0.0:
            gross_profit = gross_profit + row['profit']
            won_trades += 1
            if largest_win < row['profit']:
                largest_win = row['profit']
        else:
            gross_lost = gross_lost + row['profit']
            lost_trades += 1
            if largest_lost > row['profit']:
                largest_lost = row['profit']

    daily_return = net_profit / duration_days
    monthly_return = net_profit / (duration_days / 31)
    yearly_return = net_profit / (duration_days / 365)
    win_rate = (won_trades / total_trades) * 100
    win_loss = gross_profit / (gross_lost * - 1.0)

    result = {
        "index": a + '-' + str(b) + '-' + c + '-' + str(timespan),
        "ticker": a,
        "timeframe": b,
        "type": c,
        "first_signal": first_signal,
        # "duration": duration,
        "duration_days": duration_days,
        "net_profit": net_profit,
        "gross_profit": gross_profit,
        "gross_lost": gross_lost,
        "daily_return": daily_return,
        "monthly_return": monthly_return,
        "yearly_return": yearly_return,
        "buy_hold": buy_hold,
        "total_trades": int(total_trades),
        "won_trades": won_trades,
        "lost_trades": lost_trades,
        "win_rate": float(win_rate),
        "win_loss_ratio": win_loss,
        "largest_win": largest_win,
        "largest_lost": largest_lost
    }

    return result


# Main method
# ------------------------------------------------------------------------------

async def run2():
    async for (symbol, ticker) in run_map_trade(
            [["BTCUSD", 480], ["BTCUSD", 720], ["BTCUSD", 1], ["ETHUSD", 720], ["ETHBTC", 720], ["LINKUSD", 720],
             ["LINKBTC", 720], ["XRPUSD", 720], ["LTCUSD", 720], ["ADAUSD", 720]]):
        print(symbol, ticker)
    trades_latest = pd.DataFrame.from_dict(transform_cursor(t.find({}))).sort_values(by="date",
                                                                                     ascending=False).iloc[:3]
    # print(trades_latest)
    tl.delete_many({})
    tl.insert_many(json.loads(trades_latest.T.to_json()).values())
    trades_best = pd.DataFrame.from_dict(transform_cursor(t.find({}))).sort_values(by="current_profit",
                                                                                   ascending=False).iloc[:3]
    # print(trades_best)
    tb.delete_many({})
    tb.insert_many(json.loads(trades_best.T.to_json()).values())


async def run1(results=results):
    async for (symbol, ticker) in run_map_performance(
            [["BTCUSD", 480], ["BTCUSD", 720], ["BTCUSD", 1], ["ETHUSD", 720], ["ETHBTC", 720], ["LINKUSD", 720],
             ["LINKBTC", 720], ["XRPUSD", 720], ["LTCUSD", 720], ["ADAUSD", 720]]):
        print(symbol, ticker)
    res = pd.DataFrame.from_dict(results)
    results_sum = res[
        ["duration_days", "net_profit", "gross_profit", "daily_return", "monthly_return", "yearly_return",
         "buy_hold", "win_rate", "win_loss_ratio", "largest_win"]].copy().max().to_frame().T
    results_sum["first_signal"] = res[["first_signal"]].copy().min().to_frame().T
    results_sum["largest_lost"] = res[["largest_lost"]].copy().min().to_frame().T
    results_sum["gross_lost"] = res[["gross_lost"]].copy().min().to_frame().T
    results_sum["total_trades"] = res["total_trades"].sum()
    results_sum["won_trades"] = res["won_trades"].sum()
    results_sum["lost_trades"] = res["lost_trades"].sum()
    results_sum["index"] = "summary"
    results_sum = results_sum[
        ['index', 'first_signal', 'duration_days', 'net_profit', 'gross_profit', 'gross_lost',
         'daily_return', 'monthly_return', 'yearly_return', 'buy_hold', 'total_trades', 'won_trades', 'lost_trades',
         'win_rate', 'win_loss_ratio', 'largest_win', 'largest_lost']]
    res = res.append(results_sum).sort_values(by="index", ascending=True).reset_index()

    p.delete_many({})
    p.insert_many(json.loads(res.T.to_json()).values())

    # results_importent = res[
    #    ['index', 'duration_days', 'total_trades', 'buy_hold', 'net_profit', 'daily_return', 'win_rate',
    #     'win_loss_ratio']].copy()
    # results_importent = results_importent.sort_values(by=['net_profit'], ascending=False)
    # with pd.option_context('display.max_rows', None, 'display.max_columns',
    #                       None):  # more options can be specified also
    #    print(results_importent)


# Run async event loop
# ------------------------------------------------------------------------------

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(run2())
    loop.create_task(run1())
    loop.run_until_complete(asyncio.wait([run2(), run1()]))


main()
print("--- %s seconds ---" % (time.time() - start_time))
