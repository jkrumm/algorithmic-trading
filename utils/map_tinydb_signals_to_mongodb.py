import pymongo
from tinydb import TinyDB, Query

db = TinyDB('db.json')
signalDB = db.table('signal')

# db = client.test_database

# print(signalDB.all())
