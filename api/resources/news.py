from datetime import datetime

from flask import request
from flask_restful import Resource
from flask_restful import reqparse

import config
from src.database import news_db_col


class News(Resource):
    def get(self):
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token != config.token:
            return {'error': 'Authorization failed'}, 401
        parser = reqparse.RequestParser()
        parser.add_argument('source', required=False)
        parser.add_argument('limit', type=int, required=True)
        parser.add_argument('offset', type=int, required=True)
        args = parser.parse_args()

        news = []

        if args.get('source'):
            cursor = news_db_col.find({'source': args['source']}, {'_id': 0}).skip(args['offset']).limit(args['limit'])
        else:
            cursor = news_db_col.find({}, {'_id': 0}).skip(args['offset']).limit(args['limit'])

        for i in cursor:
            if isinstance(i["datetime"], datetime):
                i["datetime"] = i["datetime"].isoformat()
            news.append(i)
        return news, 200
