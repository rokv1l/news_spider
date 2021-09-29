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
        parser.add_argument('limit', type=int, required=True)
        parser.add_argument('offset', type=int, required=True)
        parser.add_argument('filter', type=str)
        parser.add_argument('filter_by_field', type=str)
        args = parser.parse_args()
        news = []

        if args.get('filter') and args.get('filter_by_field') not in ['source', 'url', 'title', 'content', 'datetime']:
            return {'content': 'filter_by_field must be required correctly if filter is defined'}, 400
        elif args.get('filter') and args.get('filter_by_field'):
            cursor = news_db_col.find({args.get('filter_by_field'): {"$regex": f"(?i).*{args.get('filter')}.*"}}, {'_id': 0}).skip(args['offset']).limit(args['limit'])
        else:
            cursor = news_db_col.find({}, {'_id': 0}).skip(args['offset']).limit(args['limit'])

        for i in cursor:
            if isinstance(i["datetime"], datetime):
                i["datetime"] = i["datetime"].isoformat()
            news.append(i)
        return news, 200

