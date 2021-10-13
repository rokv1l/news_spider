import re
from datetime import datetime

import pymorphy2
from flask import request
from flask_restful import Resource
from flask_restful import reqparse
from natasha import (
    Segmenter,

    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,

    Doc
)

import config
from src.database import news_db_col

segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)


def get_entities(text):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)
    return doc.spans


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


class NewsEntities(Resource):
    def get(self):
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token != config.token:
            return {'error': 'Authorization failed'}, 401
        parser = reqparse.RequestParser()
        parser.add_argument('date', type=str, required=True)
        args = parser.parse_args()

        cursor = news_db_col.find(
            {'datetime': {"$regex": f"(?i).*{args.get('date')}.*"}},
            {'_id': 0}
        )
        result = set()
        for article in cursor:
            result.update(set([entity.text for entity in get_entities(article['content'])]))
        return list(result), 200


class NewsTags(Resource):
    def get(self):
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token != config.token:
            return {'error': 'Authorization failed'}, 401
        parser = reqparse.RequestParser()
        parser.add_argument('date', type=str, required=True)
        args = parser.parse_args()
        morph = pymorphy2.MorphAnalyzer()

        cursor = news_db_col.find(
            {'datetime': {"$regex": f"(?i).*{args.get('date')}.*"}},
            {'_id': 0}
        )
        words = list()
        for article in cursor:
            text = article['content']
            for word in text.split(' '):
                processed_word = morph.parse(re.sub(pattern=r'[,!?\.«»\n]', repl='', string=word))[0]
                if processed_word.tag.POS not in ('NOUN', 'ADJF', 'ADJS', 'VERB', 'INFN'):
                    continue
                words.append(processed_word.normal_form)
        result = {}
        for word in set(words):
            result[word] = words.count(word)
        return result, 200
