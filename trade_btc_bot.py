import sys

import ccxt
import json
import time

from config import MY_BTC_TELEGRAM_TOKEN, MY_BTC_TELEGRAM_ID, kraken_users, ENV
import requests


def trade_btc_bot(action, user):
    try:
        trade_btc_bot_telegram_bot_sendtext("Execute trade btc bot : " + action + " | " + user['name'])
        start_time = time.time()

        kraken = ccxt.kraken({
            'apiKey': user['key'],
            'secret': user['secret'],
            'enableRateLimit': True,
            "timeout": 100000,
            # 'verbose': True,
            'options': {
                'fetchMinOrderAmounts': False
            }
        })

        kraken.check_required_credentials()

        output = {
            'user': user['name'],
            'btc_price': 0,
            'balance': {},
            'settle_position': {},
            'trade': {},
            'new_balance': {},
            'time': 0
        }

        kraken.load_markets()
        balance_usd = update_balance_usd(kraken)
        balance_btc = update_balance_btc(kraken)

        if balance_btc > 0.0:
            output = {
                'btc_price': 0,
                'balance': {},
                'sell_order_btc': {},
                'sell_order_btc_balance': {},
                'settle_position': {},
                'trade': {},
                'new_balance': {}
            }

        output['balance'] = balance_dict(balance_usd, balance_btc)

        trades = kraken.fetch_my_trades(symbol=None, since=kraken.parse8601('2021-01-26 00:00:00'), limit=None)
        open_order = {}
        for pos in trades:
            if 'posstatus' in pos['info'] and pos['info']['posstatus'] == 'open':
                open_order = pos

        if balance_btc > 0.0:
            output['sell_order_btc'] = kraken.create_order(
                'BTC/USD', 'market', 'sell', balance_btc)['info']['descr']['order']
            balance_usd = update_balance_usd(kraken)
            balance_btc = update_balance_btc(kraken)
            output['sell_order_balance'] = balance_dict(balance_usd, balance_btc)

        if open_order != {}:
            open_order_type = open_order['info']['type']
            open_order_vol = open_order['info']['vol']

            if open_order_type == 'buy':
                output['settle_position'] = kraken.create_order(
                    'BTC/USD', 'market', 'sell', open_order_vol, None, {'leverage': 3})['info']['descr']['order']
            else:
                output['settle_position'] = kraken.create_order(
                    'BTC/USD', 'market', 'buy', open_order_vol, None, {'leverage': 2})['info']['descr']['order']

        btc_price = kraken.fetch_ticker('BTC/USD')['close']
        output['btc_price'] = btc_price
        balance_usd = update_balance_usd(kraken)

        if action == 'buy':
            output['trade'] = kraken.create_market_buy_order(
                'BTC/USD', (balance_usd * 3 * 0.7) / btc_price,
                {
                    'leverage': 3
                }
            )['info']['descr']['order']
        else:
            output['trade'] = kraken.create_market_sell_order(
                'BTC/USD', (balance_usd * 2 * 0.5) / btc_price,
                {
                    'leverage': 2
                }
            )['info']['descr']['order']

        balance_usd = update_balance_usd(kraken)
        balance_btc = update_balance_btc(kraken)
        output['new_balance'] = balance_dict(balance_usd, balance_btc)
        output['time'] = time.time() - start_time
        print(str(json.dumps(output, indent=2)))
        output_str = '🤖📈 BUY | ' + ENV if action == "buy" else '🤖📉 SELL | ' + ENV + " | "
        output_str += str(output['user']) + " | " + str(output['trade']) + " | "
        output_str += str(round(output['new_balance']['USD'], 2)) + "$"
        trade_btc_bot_telegram_bot_sendtext(output_str)
        trade_btc_bot_telegram_bot_sendtext(str(output))
        return output
    except Exception as e:
        print(e)
        trade_btc_bot_telegram_bot_sendtext("Exception executing trade : " + user['name'])
        trade_btc_bot_telegram_bot_sendtext(str(e))
        return e


def trade_btc_bot_telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + MY_BTC_TELEGRAM_TOKEN + '/sendMessage?chat_id=' + MY_BTC_TELEGRAM_ID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


def balance_dict(balance_usd, balance_btc):
    return {'USD': balance_usd, 'BTC': balance_btc}


def update_balance_btc(kraken):
    return float(kraken.fetch_balance()["info"]['XXBT'])


def update_balance_usd(kraken):
    return float(kraken.fetch_balance()["info"]['ZUSD'])


def run_trade_btc_bot(action):
    results = []
    for user in kraken_users:
        results.append(trade_btc_bot(action, user))
    trade_btc_bot_telegram_bot_sendtext(str(results))
