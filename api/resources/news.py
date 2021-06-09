import json

from flask import request
from flask_restful import Resource
from flask_restful import reqparse

import config
from src.database import news_db_col


class GetNews(Resource):
    def get(self):
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token != config.token:
            return {'error': 'Authorization failed, wrong token'}, 401
        parser = reqparse.RequestParser()
        parser.add_argument('source', required=True)
        args = parser.parse_args()
        news = list(news_db_col.find({'source': args['source']}, {'_id': 0}))
        if not news:
            return {'error': 'Not results, may be you select wrong source'}, 404
        else:
            return news, 200
