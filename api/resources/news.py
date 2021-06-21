from datetime import datetime

from flask import request
from flask_restful import Resource
from flask_restful import reqparse

import config
from src.database import news_db_col


class News(Resource):
    def get(self):
        print('news connection')
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token != config.token:
            return {'error': 'Authorization failed'}, 401
        parser = reqparse.RequestParser()
        parser.add_argument('source', required=False)
        args = parser.parse_args()

        news = []

        if args.get('source'):
            cursor = news_db_col.find({'source': args['source']}, {'_id': 0})
        else:
            cursor = news_db_col.find({}, {'_id': 0})

        for i in cursor:
            try:
                if isinstance(i["datetime"], datetime):
                    i["datetime"] = i["datetime"].isoformat()
            except Exception:
                print('-------------------------------------------------------------------------------------')
                print(i)
                print('-------------------------------------------------------------------------------------')
            news.append(i)
        print('done')
        return news, 200
