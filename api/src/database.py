from pymongo import MongoClient
from pymongo.collection import Collection

from config import mongo_ip, mongo_port

client = MongoClient(mongo_ip, mongo_port)
db = client.news_parser
news_db_col: Collection = db.news