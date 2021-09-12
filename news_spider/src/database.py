from pymongo import MongoClient

from config import mongo_ip, mongo_port

client = MongoClient(mongo_ip, mongo_port)
db = client.news_parser
news_db_col = db.news
changed_news_col = db.changed_news
errors_db_col = db.errors
