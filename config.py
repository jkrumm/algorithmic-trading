import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, "algorithmic-trading", ".env"))

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
SECRET_KEY = os.getenv("SECRET_KEY")
# DW_PW = os.getenv("DW_PW")
MONGO_URI = "mongodb+srv://application:" + os.getenv(
    "DB_PW") + "@cluster0.adwbt.mongodb.net/<dbname>?retryWrites=true&w=majority"
NOMICS_KEY = os.getenv("NOMICS_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
