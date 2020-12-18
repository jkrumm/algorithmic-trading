# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from flask import Flask, render_template, request, jsonify
from tinydb import TinyDB, Query
import logging
from logging import Formatter, FileHandler

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')

db = TinyDB('db.json')

signalDB = db.table('signal')
Ticker = Query()


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html', signal=signalDB.all())


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/test/v1/postSignal', methods=['POST'])
def test_post_signal_v1():
    content = request.get_json()
    print(request.get_json())
    content['ticker'] = content['ticker'].replace('XBT', 'BTC')
    signalDB.insert(content)
    return jsonify(content)


@app.route('/test/v1/getSignal/<ticker>', methods=['GET'])
def test_get_signal_v1(ticker):
    if ticker == "all":
        return jsonify(signalDB.all())
    else:
        return jsonify(signalDB.search(Ticker.ticker == ticker))


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
