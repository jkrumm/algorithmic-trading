# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import os
from datetime import datetime

import dateutil.parser as parser
from flask import Flask, render_template, request, jsonify
from flask_fontawesome import FontAwesome
import logging
from logging import Formatter, FileHandler
from flask_pymongo import PyMongo

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
from config import SECRET_KEY
from utils.helper import transform_cursor, telegram_bot_sendtext, transform_interval, twitter_init, tweet, \
    map_currencies_to_dict, transform_cursor_dict

app = Flask(__name__)
app.config.from_object('config')
fa = FontAwesome(app)
m = PyMongo(app).db
twitter = twitter_init()


# from backtesting import Backtest, Strategy
# from backtesting.lib import crossover

# from backtesting.test import SMA, GOOG


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

# class SmaCross(Strategy):
#     def init(self):
#         price = self.data.Close
#         self.ma1 = self.I(SMA, price, 10)
#         self.ma2 = self.I(SMA, price, 20)
#
#     def next(self):
#         if crossover(self.ma1, self.ma2):
#             self.buy()
#         elif crossover(self.ma2, self.ma1):
#             self.sell()


# bt = Backtest(GOOG, SmaCross, commission=.002, exclusive_orders=True)
# stats = bt.run()
# bt.plot(filename="./static/backtest/SmaCross.html")

# v=spf1 ip4:66.96.128.0/18 ?all
# google-site-verification=hnZDTIZDro-SF5tDbwG_MyeEL0wCbgKVBG9YRyjxf18

@app.route('/')
def home():
    symbol = request.args.get('symbol')
    interval = request.args.get('interval')
    action = request.args.get('action')
    timespan = request.args.get('timespan')
    signal = []

    if symbol is None:
        symbol = "ETHUSD"
    if interval is None:
        interval = "720"
    if action is None:
        action = "buy_sell"
    if timespan is None:
        timespan = "0"

    if action == "buy_sell":
        signal = m.signals.find({"ticker": symbol, "interval": interval})
    else:
        signal = m.signals.find({"ticker": symbol, "interval": interval, "action": action})

    signal = transform_cursor(signal)

    if timespan != "0":
        date_now = parser.parse(datetime.now().isoformat()[:19].replace('T', ' '))
        new_signal = []
        for x in signal:
            if abs(date_now - parser.parse(x["time"][:19].replace('T', ' '))).days < int(timespan):
                new_signal.append(x)
        signal = new_signal

    print(transform_cursor_dict(
        m.performance.find_one({"index": symbol + "-" + interval + "-" + action + "-" + timespan})))

    return render_template('pages/placeholder.home.html',
                           args=request.args,
                           trades=m.trades.find(),
                           signal=signal,
                           performance=transform_cursor_dict(m.performance.find_one(
                               {"index": symbol + "-" + interval + "-" + action + "-" + timespan})),
                           currencies=map_currencies_to_dict(m.currencies.find()))


@app.route('/marketcap')
def marketcap():
    return render_template('pages/marketcap.html', args=request.args,
                           currencie=map_currencies_to_dict(m.currencies.find()))


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/contact')
def contact():
    return render_template('pages/contact.html')


@app.route('/tweet/<msg>')
def tweet_endpoint(msg):
    return tweet(twitter, msg)


@app.route('/postSignal', methods=['POST'])
def test_post_signal_v1():
    content = request.get_json()
    print(request.get_json())
    if content['secret'] != SECRET_KEY:
        return "Unauthorized"
    content['ticker'] = content['ticker'].replace('XBT', 'BTC')
    m.signals.insert_one(content)
    if '_id' in content: del content['_id']
    print(content)
    str = '🤖📈 BUY | ' if content['action'] == "buy" else '🤖📉 SELL | '
    str_twitter = str
    str += content['ticker'] + ' | ' + transform_interval(content['interval']) + ' | ' + "{:.2f}".format(
        float(content['price'])) + "$"
    content['telegram'] = str
    telegram_bot_sendtext(str)
    str_twitter += '$' + content['ticker'] + ' | ' + transform_interval(content['interval']) + ' | ' + "{:.2f}".format(
        float(content['price'])) + "$"
    str_twitter += '\n' + '\n' + "All signals and performance on AlgorithmicCrypto.com"
    str_twitter += '\n' + "$" + content['ticker'][:-3] + " #trading #bot #signal #automated #cryptocurrency"
    content['twitter'] = str_twitter
    tweet(twitter, str_twitter)
    return jsonify(content)


@app.route('/postTelegram', methods=['POST'])
def postTelegram():
    content = request.get_json()
    print(request.get_json())
    if content['secret'] != SECRET_KEY:
        return "Unauthorized"
    telegram_bot_sendtext(content['msg'])
    return jsonify(content)


@app.route('/test/v1/getSignal/<ticker>', methods=['GET'])
def test_get_signal_v1(ticker):
    if ticker == "all":
        print(list(m.signals.find({})))
        return jsonify(m.signals.find({}))
    else:
        return jsonify(transform_cursor(m.signals.find({"ticker": ticker})))


@app.route('/test/v1/getCurrency/<ticker>', methods=['GET'])
def test_get_currency_v1(ticker):
    print(ticker)
    if ticker == "all":
        print(list(m.currencies.find({})))
        return jsonify(list(transform_cursor(m.currencies.find({}))))
    else:
        print(transform_cursor(m.currencies.find({"currency": ticker}))[0])
        return jsonify(transform_cursor(m.currencies.find({"currency": ticker}))[0])


# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run()
