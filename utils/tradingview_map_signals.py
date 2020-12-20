import dateutil.parser as parser
import pandas as pd

pd.options.mode.chained_assignment = None
import numpy as np
from tinydb import TinyDB, Query

db = TinyDB('../db.json')
signalDB = db.table('signal')
q = Query()

df = pd.read_csv('BTCUSD_8H.csv')
ticker = "BTCUSD"
interval = "480"
# interval = "720"
# interval = "1"

# signalDB.remove((q.ticker == ticker) & (q.interval == str(interval)))

df = df[df['Trade #'].notnull()].reset_index()[['Signal', 'Date/Time', 'Price']]

df['Signal'] = np.where((df.Signal == 'Enter Long'), 'buy', df.Signal)
df['Signal'] = np.where((df.Signal == 'Enter Short'), 'sell', df.Signal)
df['profit'] = 0.00

for index, row in df.iterrows():
    if index > 0:
        val = ((df.iloc[index]['Price'] - df.iloc[index - 1]['Price']) / df.iloc[index - 1]['Price']) * 100.00
        if df.at[index - 1, 'Signal'] == "buy":
            df.at[index - 1, 'profit'] = val
        else:
            df.at[index - 1, 'profit'] = val * -1
    val2 = str(parser.parse(row['Date/Time']).isoformat())
    df.at[index, 'Date/Time'] = val2

print(df.head(5))

duplicates = []

for index, row in df.iterrows():
    if len(signalDB.search(
            (q.time == row['Date/Time']) & (q.ticker == ticker) & (q.interval == interval))) > 0:
        duplicates.append(index)
    else:
        signalDB.insert({
            "ticker": ticker.replace('XBT', 'BTC'),
            "exchange": "KRAKEN",
            "interval": interval,
            "time": row['Date/Time'],
            "action": row['Signal'],
            "price": row['Price'],
            "profit": row['profit']
        })
if len(duplicates) > 0:
    print("Duplicate found! Index:")
    print(duplicates)
else:
    print("Successful insert: " + str(index))
