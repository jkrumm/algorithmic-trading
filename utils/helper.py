import requests
from config import BOT_TOKEN, CHAT_ID


def transform_cursor(obj):
    data = list(obj)
    for x in data:
        if '_id' in x: del x['_id']
    return data


def transform_cursor_dict(obj):
    if '_id' in obj: del obj['_id']
    return obj


def transform_interval(n):
    if int(n) == 480:
        return '8H'
    if int(n) == 720:
        return '12H'
    if int(n) == 1:
        return '1D'


def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + CHAT_ID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()
