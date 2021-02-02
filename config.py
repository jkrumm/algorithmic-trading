import json
import os
from dotenv import load_dotenv
from utils.secrets import get_kraken_users

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, "algorithmic-trading", ".env"))

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY_TRADE_BTC = os.getenv("SECRET_KEY_TRADE_BTC")
MY_KRAKEN_DE_KEY = os.getenv("MY_KRAKEN_DE_KEY")
MY_KRAKEN_DE_SECRET = os.getenv("MY_KRAKEN_DE_SECRET")
MY_BTC_TELEGRAM_TOKEN = os.getenv("MY_BTC_TELEGRAM_TOKEN")
MY_BTC_TELEGRAM_ID = os.getenv("MY_BTC_TELEGRAM_ID")
# DW_PW = os.getenv("DW_PW")
MONGO_URI = "mongodb+srv://application:" + os.getenv(
    "DB_PW") + "@cluster0.adwbt.mongodb.net/<dbname>?retryWrites=true&w=majority"
NOMICS_KEY = os.getenv("NOMICS_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
consumer_key = os.getenv("consumer_key")
consumer_secret = os.getenv("consumer_secret")
access_token = os.getenv("access_token")
access_token_secret = os.getenv("access_token_secret")

kraken_users = get_kraken_users()
