import logging
import re
from datetime import datetime
from collections import Counter

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
from config import get_logger, logs_path
from src.database import news_db_col

logger = get_logger(__name__, logs_path + __name__ + '.log', backups=2)

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
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('limit', type=int, required=True)
            parser.add_argument('offset', type=int, required=True)
            parser.add_argument('query')
            parser.add_argument('response')

            args = parser.parse_args()
            logger.debug(f'{request.remote_addr} News.get params {args}')

            if args.get('query') and args.get('response'):
                args['response']['_id'] = 0
                news = news_db_col.find(args.get('query'), args.get('response')).skip(args['offset']).limit(args['limit'])
            else:
                news = news_db_col.find({}, {'_id': 0}).skip(args['offset']).limit(args['limit'])

            result = []
            for article in news:
                if isinstance(article['datetime'], datetime):
                    article['datetime'] = article['datetime'].isoformat()
                result.append(article)
        except Exception:
            logger.exception('{request.remote_addr} Request ip. Args - {args}')
            raise

        logger.debug('{request.remote_addr} News.get OK 200. Response {len(result)} news')
        return result, 200


class NewsEntities(Resource):
    def get(self):
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token != config.token:
            return {'error': 'Authorization failed'}, 401
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('date', type=str, required=True)
            parser.add_argument('limit', type=int, required=True)

            args = parser.parse_args()
            logger.debug(f'{request.remote_addr} NewsEntities.get params {args}')

            cursor = news_db_col.find(
                {'datetime': {"$regex": f"(?i).*{args.get('date')}.*"}},
                {'_id': 0}
            )
            result = list()
            for article in cursor:
                result.extend([entity.text for entity in get_entities(article['content'])])
            
            result = Counter(result)
            # сортировка по количеству вхождений
            result = sorted(result.items(), key=lambda item: item[1], reverse=True)
            # обрезка по лимиту
            result = dict(result[:args['limit']])
        except Exception:
            logger.exception('{request.remote_addr} Request ip. Args - {args}')
            raise
            
        logger.debug('{request.remote_addr} NewsEntities.get OK 200. Response {len(result)} news')
        return result, 200


class NewsTags(Resource):
    def get(self):
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token != config.token:
            return {'error': 'Authorization failed'}, 401

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('date', type=str, required=True)
            parser.add_argument('limit', type=int, required=True)

            args = parser.parse_args()
            logger.debug(f'{request.remote_addr} NewsTags.get params {args}')
            
            # TODO Сделать проверку args.get('date') на соответствие формату date и datetime
            cursor = news_db_col.find(
                {'datetime': {"$regex": f"(?i).*{args.get('date')}.*"}},
                {'_id': 0}
            )
            result = list()
            
            morph = pymorphy2.MorphAnalyzer()
            for article in cursor:
                text = re.sub(pattern=r'[^a-zA-Zа-яА-Я ]', repl='', string=article['content'])
                for word in text.split(' '):
                    if not word.isalpha():
                        continue

                    processed_word = morph.parse(word)[0]
                    if processed_word.tag.POS not in ('NOUN', 'ADJF', 'ADJS', 'VERB', 'INFN'):
                        continue

                    result.append(processed_word.normal_form)

            result = Counter(result)
            # сортировка по значению
            result = sorted(result.items(), key=lambda item: item[1], reverse=True)
            # обрезка по лимиту
            result = dict(result[:args['limit']])
        except Exception:
            logger.exception('{request.remote_addr} Request ip. Args - {args}')
            raise

        logger.debug('{request.remote_addr} NewsTags.get OK 200. Response {len(result)} news')
        return result, 200
