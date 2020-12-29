import os
import sys

# -----------------------------------------------------------------------------
from datetime import datetime

import dateutil.parser

this_folder = os.path.dirname(os.path.abspath(__file__))
root_folder = os.path.dirname(os.path.dirname(this_folder))
sys.path.append(root_folder + '/python')
sys.path.append(this_folder)

# -----------------------------------------------------------------------------

import ccxt  # noqa: E402

# -----------------------------------------------------------------------------

exchange = ccxt.kraken()
symbol = 'ETH/USD'

# each ohlcv candle is a list of [ timestamp, open, high, low, close, volume ]
index = 4  # use close price from each ohlcv candle

# length = 80
# height = 15

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG

import pandas as pd

pd.options.mode.chained_assignment = None
import numpy as np


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

class SmaCross(Strategy):
    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.signals = [
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 1.34, "profit": -10.44776119402986,
             "ticker": "ETHUSD", "time": "2015-09-02T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 1.2, "profit": 49.166666666666664,
             "ticker": "ETHUSD", "time": "2015-09-11T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 0.61, "profit": 45.9016393442623,
             "ticker": "ETHUSD", "time": "2015-10-26T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 0.89, "profit": -7.865168539325837,
             "ticker": "ETHUSD", "time": "2015-11-07T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 0.96, "profit": -8.33333333333333,
             "ticker": "ETHUSD", "time": "2015-11-09T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 0.88, "profit": -9.090909090909086,
             "ticker": "ETHUSD", "time": "2015-11-12T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 0.96, "profit": -7.291666666666662,
             "ticker": "ETHUSD", "time": "2015-11-19T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 0.89, "profit": -2.247191011235957,
             "ticker": "ETHUSD", "time": "2015-11-26T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 0.91, "profit": -3.2967032967032996,
             "ticker": "ETHUSD", "time": "2015-12-13T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 0.88, "profit": -5.681818181818187,
             "ticker": "ETHUSD", "time": "2015-12-24T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 0.93, "profit": 365.59139784946234,
             "ticker": "ETHUSD", "time": "2016-01-01T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 4.33, "profit": -15.704387990762116,
             "ticker": "ETHUSD", "time": "2016-02-19T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 5.01, "profit": 107.18562874251501,
             "ticker": "ETHUSD", "time": "2016-02-23T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 10.38, "profit": -12.8131021194605,
             "ticker": "ETHUSD", "time": "2016-03-19T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 11.71, "profit": -6.575576430401378,
             "ticker": "ETHUSD", "time": "2016-03-24T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 10.94, "profit": -5.575868372943338,
             "ticker": "ETHUSD", "time": "2016-03-26T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 11.55, "profit": -3.549783549783551,
             "ticker": "ETHUSD", "time": "2016-03-30T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 11.14, "profit": 18.850987432675055,
             "ticker": "ETHUSD", "time": "2016-04-05T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 9.04, "profit": -5.97345132743362,
             "ticker": "ETHUSD", "time": "2016-04-19T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 8.5, "profit": -0.8235294117647093,
             "ticker": "ETHUSD", "time": "2016-04-22T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 8.57, "profit": 44.34072345390897,
             "ticker": "ETHUSD", "time": "2016-05-02T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 12.37, "profit": -8.569118835893295,
             "ticker": "ETHUSD", "time": "2016-05-27T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 13.43, "profit": -3.2762472077438534,
             "ticker": "ETHUSD", "time": "2016-06-01T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 12.99, "profit": -8.468052347959967,
             "ticker": "ETHUSD", "time": "2016-06-19T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 14.09, "profit": -5.2519517388218615,
             "ticker": "ETHUSD", "time": "2016-06-27T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 13.35, "profit": 14.007490636704114,
             "ticker": "ETHUSD", "time": "2016-06-29T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 11.48, "profit": 10.975609756097558,
             "ticker": "ETHUSD", "time": "2016-07-15T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 12.74, "profit": 8.39874411302983,
             "ticker": "ETHUSD", "time": "2016-07-30T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 11.67, "profit": -3.856041131105392,
             "ticker": "ETHUSD", "time": "2016-08-10T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 11.22, "profit": -0.17825311942958622,
             "ticker": "ETHUSD", "time": "2016-08-16T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 11.24, "profit": -1.7793594306049918,
             "ticker": "ETHUSD", "time": "2016-08-26T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 11.04, "profit": -2.445652173913056,
             "ticker": "ETHUSD", "time": "2016-08-30T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 11.31, "profit": 1.8567639257294346,
             "ticker": "ETHUSD", "time": "2016-09-01T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 11.52, "profit": -2.256944444444443,
             "ticker": "ETHUSD", "time": "2016-09-09T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 11.78, "profit": 10.016977928692713,
             "ticker": "ETHUSD", "time": "2016-09-11T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 12.96, "profit": 3.8580246913580245,
             "ticker": "ETHUSD", "time": "2016-10-07T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 12.46, "profit": -3.4510433386838,
             "ticker": "ETHUSD", "time": "2016-10-19T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 12.03, "profit": 30.75644222776392,
             "ticker": "ETHUSD", "time": "2016-10-25T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 8.33, "profit": -5.40216086434574,
             "ticker": "ETHUSD", "time": "2016-12-10T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 7.88, "profit": -1.52284263959391,
             "ticker": "ETHUSD", "time": "2016-12-17T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 8, "profit": 21.625000000000007,
             "ticker": "ETHUSD", "time": "2016-12-30T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 9.73, "profit": -4.4193216855087325,
             "ticker": "ETHUSD", "time": "2017-01-14T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 10.16, "profit": 3.2480314960629926,
             "ticker": "ETHUSD", "time": "2017-01-18T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 10.49, "profit": -1.620591039084842,
             "ticker": "ETHUSD", "time": "2017-01-30T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 10.66, "profit": 320.8255159474672,
             "ticker": "ETHUSD", "time": "2017-02-01T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 44.86, "profit": -6.107891217119933,
             "ticker": "ETHUSD", "time": "2017-04-04T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 47.6, "profit": 587.8991596638655,
             "ticker": "ETHUSD", "time": "2017-04-14T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 327.44, "profit": 33.13889567554361,
             "ticker": "ETHUSD", "time": "2017-06-22T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 218.93, "profit": -6.846937377243872,
             "ticker": "ETHUSD", "time": "2017-07-21T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 203.94, "profit": -6.972639011473962,
             "ticker": "ETHUSD", "time": "2017-07-27T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 218.16, "profit": 48.76237623762377,
             "ticker": "ETHUSD", "time": "2017-08-02T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 324.54, "profit": 12.192641893141058,
             "ticker": "ETHUSD", "time": "2017-09-05T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 284.97, "profit": -5.779555742709768,
             "ticker": "ETHUSD", "time": "2017-09-21T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 268.5, "profit": -4.517690875232773,
             "ticker": "ETHUSD", "time": "2017-09-23T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 280.63, "profit": 4.397249046787596,
             "ticker": "ETHUSD", "time": "2017-09-24T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 292.97, "profit": -2.3927364576577776,
             "ticker": "ETHUSD", "time": "2017-10-06T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 299.98, "profit": 3.250216681112074,
             "ticker": "ETHUSD", "time": "2017-10-07T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 309.73, "profit": 1.4851644981112655,
             "ticker": "ETHUSD", "time": "2017-10-20T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 305.13, "profit": -5.040474551830366,
             "ticker": "ETHUSD", "time": "2017-10-31T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 289.75, "profit": -3.8239861949956806,
             "ticker": "ETHUSD", "time": "2017-11-03T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 300.83, "profit": 41.02316923179205,
             "ticker": "ETHUSD", "time": "2017-11-09T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 424.24, "profit": -5.407316613237789,
             "ticker": "ETHUSD", "time": "2017-12-08T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 447.18, "profit": 47.464108412719696,
             "ticker": "ETHUSD", "time": "2017-12-11T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 659.43, "profit": -12.372806818009499,
             "ticker": "ETHUSD", "time": "2017-12-25T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 741.02, "profit": 35.992280910096895,
             "ticker": "ETHUSD", "time": "2017-12-27T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 1007.73, "profit": -10.48495132624811,
             "ticker": "ETHUSD", "time": "2018-01-18T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 1113.39, "profit": -10.807533748282285,
             "ticker": "ETHUSD", "time": "2018-01-28T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 993.06, "profit": 12.041568485287891,
             "ticker": "ETHUSD", "time": "2018-02-02T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 873.48, "profit": -4.2233365389018624,
             "ticker": "ETHUSD", "time": "2018-02-15T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 836.59, "profit": 51.200707634564125,
             "ticker": "ETHUSD", "time": "2018-02-23T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 408.25, "profit": 71.69381506429885,
             "ticker": "ETHUSD", "time": "2018-04-11T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 700.94, "profit": 13.140925043512997,
             "ticker": "ETHUSD", "time": "2018-05-12T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 608.83, "profit": -7.21876385854837,
             "ticker": "ETHUSD", "time": "2018-06-04T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 564.88, "profit": 5.762285795213135,
             "ticker": "ETHUSD", "time": "2018-06-11T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 532.33, "profit": -9.648150583284806,
             "ticker": "ETHUSD", "time": "2018-06-21T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 480.97, "profit": 3.0105827806308123,
             "ticker": "ETHUSD", "time": "2018-06-23T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 466.49, "profit": -4.844691204527432,
             "ticker": "ETHUSD", "time": "2018-07-04T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 443.89, "profit": -5.564441640947079,
             "ticker": "ETHUSD", "time": "2018-07-11T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 468.59, "profit": -2.2983845152478675,
             "ticker": "ETHUSD", "time": "2018-07-17T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 457.82, "profit": -3.0448647940238516,
             "ticker": "ETHUSD", "time": "2018-07-24T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 471.76, "profit": -2.327454637951505,
             "ticker": "ETHUSD", "time": "2018-07-25T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 460.78, "profit": 36.85055774990233,
             "ticker": "ETHUSD", "time": "2018-07-31T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 290.98, "profit": -4.642930785621002,
             "ticker": "ETHUSD", "time": "2018-08-30T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 277.47, "profit": 21.425739719609332,
             "ticker": "ETHUSD", "time": "2018-09-05T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 218.02, "profit": -5.2839189065223415,
             "ticker": "ETHUSD", "time": "2018-09-17T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 206.5, "profit": -3.2687651331719128,
             "ticker": "ETHUSD", "time": "2018-09-20T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 213.25, "profit": 1.1629542790152354,
             "ticker": "ETHUSD", "time": "2018-09-21T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 215.73, "profit": -6.712093820979938,
             "ticker": "ETHUSD", "time": "2018-09-27T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 230.21, "profit": -3.9268493983754054,
             "ticker": "ETHUSD", "time": "2018-09-30T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 221.17, "profit": -2.233575982276089,
             "ticker": "ETHUSD", "time": "2018-10-04T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 226.11, "profit": -4.281102118437931,
             "ticker": "ETHUSD", "time": "2018-10-09T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 216.43, "profit": 6.154414822344403,
             "ticker": "ETHUSD", "time": "2018-10-11T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 203.11, "profit": 1.654276008074435,
             "ticker": "ETHUSD", "time": "2018-11-05T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 206.47, "profit": 52.5403206276941,
             "ticker": "ETHUSD", "time": "2018-11-14T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 97.99, "profit": 33.69731605265843,
             "ticker": "ETHUSD", "time": "2018-12-19T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 131.01, "profit": 13.31959392412792,
             "ticker": "ETHUSD", "time": "2019-01-11T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 113.56, "profit": 19.41704825642833,
             "ticker": "ETHUSD", "time": "2019-02-09T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 135.61, "profit": -0.29496349826707263,
             "ticker": "ETHUSD", "time": "2019-02-28T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 136.01, "profit": -2.705683405631923,
             "ticker": "ETHUSD", "time": "2019-03-08T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 132.33, "profit": -4.60968790145847,
             "ticker": "ETHUSD", "time": "2019-03-12T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 138.43, "profit": -1.9215487972260323,
             "ticker": "ETHUSD", "time": "2019-03-17T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 135.77, "profit": -1.1269057965677256,
             "ticker": "ETHUSD", "time": "2019-03-25T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 137.3, "profit": 19.235251274581206,
             "ticker": "ETHUSD", "time": "2019-03-29T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 163.71, "profit": -4.746197544438325,
             "ticker": "ETHUSD", "time": "2019-04-14T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 171.48, "profit": -3.364823886167473,
             "ticker": "ETHUSD", "time": "2019-04-19T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 165.71, "profit": 1.5750407338120893,
             "ticker": "ETHUSD", "time": "2019-04-25T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 163.1, "profit": 52.02942979767015,
             "ticker": "ETHUSD", "time": "2019-05-04T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 247.96, "profit": -3.4360380706565614,
             "ticker": "ETHUSD", "time": "2019-06-05T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 256.48, "profit": 14.683406113537103,
             "ticker": "ETHUSD", "time": "2019-06-14T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 294.14, "profit": -4.004895627932288,
             "ticker": "ETHUSD", "time": "2019-07-02T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 305.92, "profit": -8.358394351464431,
             "ticker": "ETHUSD", "time": "2019-07-09T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 280.35, "profit": 22.38273586588194,
             "ticker": "ETHUSD", "time": "2019-07-12T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 217.6, "profit": -3.074448529411764,
             "ticker": "ETHUSD", "time": "2019-08-03T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 210.91, "profit": 15.17708975392347,
             "ticker": "ETHUSD", "time": "2019-08-10T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 178.9, "profit": 0.19564002235885652,
             "ticker": "ETHUSD", "time": "2019-09-09T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 179.25, "profit": -0.1059972105997198,
             "ticker": "ETHUSD", "time": "2019-09-25T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 179.44, "profit": -1.0309852875612986,
             "ticker": "ETHUSD", "time": "2019-10-09T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 177.59, "profit": -1.0867729038797267,
             "ticker": "ETHUSD", "time": "2019-10-17T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 179.52, "profit": 2.785204991087344,
             "ticker": "ETHUSD", "time": "2019-10-27T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 184.52, "profit": 28.490136570561468,
             "ticker": "ETHUSD", "time": "2019-11-15T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 131.95, "profit": 21.629405077680957,
             "ticker": "ETHUSD", "time": "2019-12-30T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 160.49, "profit": -4.2619477849087195,
             "ticker": "ETHUSD", "time": "2020-01-26T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 167.33, "profit": 49.81174923803262,
             "ticker": "ETHUSD", "time": "2020-01-28T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 250.68, "profit": 3.949258018190524,
             "ticker": "ETHUSD", "time": "2020-02-26T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 240.78, "profit": -11.238474956391729,
             "ticker": "ETHUSD", "time": "2020-03-07T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 213.72, "profit": 35.97230020587684,
             "ticker": "ETHUSD", "time": "2020-03-09T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 136.84, "profit": -5.999707687810588,
             "ticker": "ETHUSD", "time": "2020-03-25T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 128.63, "profit": -5.053253517841872,
             "ticker": "ETHUSD", "time": "2020-03-30T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 135.13, "profit": 15.866202915710796,
             "ticker": "ETHUSD", "time": "2020-04-02T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 156.57, "profit": -5.492750846266842,
             "ticker": "ETHUSD", "time": "2020-04-16T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 165.17, "profit": 18.556638614760555,
             "ticker": "ETHUSD", "time": "2020-04-17T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 195.82, "profit": -3.390869165560216,
             "ticker": "ETHUSD", "time": "2020-05-11T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 202.46, "profit": 0.42477526424972106,
             "ticker": "ETHUSD", "time": "2020-05-18T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 203.32, "profit": -3.3395632500491934,
             "ticker": "ETHUSD", "time": "2020-05-26T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 210.11, "profit": 12.65527580791013,
             "ticker": "ETHUSD", "time": "2020-05-29T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 236.7, "profit": -1.1280101394169901,
             "ticker": "ETHUSD", "time": "2020-06-13T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 239.37, "profit": -3.776580189664533,
             "ticker": "ETHUSD", "time": "2020-06-23T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 230.33, "profit": -1.5542916684756583,
             "ticker": "ETHUSD", "time": "2020-06-27T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 233.91, "profit": 0.3975888162113662,
             "ticker": "ETHUSD", "time": "2020-07-07T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 234.84, "profit": -2.840231647078857,
             "ticker": "ETHUSD", "time": "2020-07-17T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 241.51, "profit": 67.42992008612481,
             "ticker": "ETHUSD", "time": "2020-07-22T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 404.36, "profit": -1.0559897121376944,
             "ticker": "ETHUSD", "time": "2020-08-22T02:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 408.63, "profit": -6.277072167975914,
             "ticker": "ETHUSD", "time": "2020-08-31T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 382.98, "profit": 2.9818789492923954,
             "ticker": "ETHUSD", "time": "2020-09-05T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 371.56, "profit": -6.171277855528046,
             "ticker": "ETHUSD", "time": "2020-09-14T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 348.63, "profit": -2.303301494421028,
             "ticker": "ETHUSD", "time": "2020-09-22T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 356.66, "profit": -2.716873212583412,
             "ticker": "ETHUSD", "time": "2020-09-30T02:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 346.97, "profit": -4.668991555465887,
             "ticker": "ETHUSD", "time": "2020-10-03T14:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 363.17, "profit": 6.925131481124536,
             "ticker": "ETHUSD", "time": "2020-10-10T14:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 388.32, "profit": -3.8164400494437563,
             "ticker": "ETHUSD", "time": "2020-10-30T01:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 403.14, "profit": 32.527161780026795,
             "ticker": "ETHUSD", "time": "2020-11-06T01:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 534.27, "profit": -5.852845939319068,
             "ticker": "ETHUSD", "time": "2020-11-29T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 565.54, "profit": -0.16444460161968208,
             "ticker": "ETHUSD", "time": "2020-11-30T13:00:00"},
            {"action": "sell", "exchange": "KRAKEN", "interval": "720", "price": 564.61, "profit": -3.4501691433024595,
             "ticker": "ETHUSD", "time": "2020-12-09T13:00:00"},
            {"action": "buy", "exchange": "KRAKEN", "interval": "720", "price": 584.09, "profit": 0, "ticker": "ETHUSD",
             "time": "2020-12-15T13:00:00"}]

    def init(self):
        price = self.data.Close

    def next(self):
        for s in self.signals:
            if s['time'] == self.data.index and s['action'] == "buy":
                self.buy()
            if s['time'] == self.data.index and s['action'] == "sell":
                self.sell()


def print_chart(exchange, symbol, timeframe):
    # get a list of ohlcv candles
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=10000000001)

    print("\n" + exchange.name + ' ' + symbol + ' ' + timeframe + ' chart:')

    df = pd.DataFrame(np.row_stack(ohlcv)).rename(
        columns={0: "Date", 1: "Open", 2: "High", 3: "Low", 4: "Close", 5: "Volume"})
    df['Date'] = df['Date'].apply(lambda x: datetime.fromtimestamp(float(x) / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f'))
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    bt = Backtest(df, SmaCross, commission=.002,
                  exclusive_orders=True)
    stats = bt.run()
    print(stats)
    bt.plot(filename="./static/backtest/SmaCross.html")

    last = ohlcv[len(ohlcv) - 1][index]  # last closing price
    return last


last = print_chart(exchange, symbol, '1h')
print("\n" + exchange.name + ' last price: ' + str(last) + "\n")  # print last closing price
