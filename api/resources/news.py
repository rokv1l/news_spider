import re
from itertools import islice

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
        parser.add_argument('query', type=dict, required=True)
        parser.add_argument('response', type=dict, required=True)
        args = parser.parse_args()
        args['response']['_id'] = 0
        news = news_db_col.find(args.get('query'), args.get('response')).skip(args['offset']).limit(args['limit'])
        return list(news), 200


class NewsEntities(Resource):
    def get(self):
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token != config.token:
            return {'error': 'Authorization failed'}, 401
        parser = reqparse.RequestParser()
        parser.add_argument('date', type=str, required=True)
        parser.add_argument('limit', type=int, required=True)
        args = parser.parse_args()

        cursor = news_db_col.find(
            {'datetime': {"$regex": f"(?i).*{args.get('date')}.*"}},
            {'_id': 0}
        )
        result = dict()
        for article in cursor:
            entities = [entity.text for entity in get_entities(article['content'])]
            for entity in entities:
                if not result.get(entity):
                    result[entity] = 0
                result[entity] += 1

        # сортировка по значению
        result = dict(reversed(sorted(result.items(), key=lambda item: item[1])))
        # обрезка по лимиту
        result = dict(islice(result.items(), args.get('limit')))
        return result, 200


class NewsTags(Resource):
    def get(self):
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token != config.token:
            return {'error': 'Authorization failed'}, 401
        parser = reqparse.RequestParser()
        parser.add_argument('date', type=str, required=True)
        parser.add_argument('limit', type=int, required=True)
        args = parser.parse_args()
        morph = pymorphy2.MorphAnalyzer()

        cursor = news_db_col.find(
            {'datetime': {"$regex": f"(?i).*{args.get('date')}.*"}},
            {'_id': 0}
        )
        result = dict()
        for article in cursor:
            text = re.sub(pattern=r'[,!?\.«»]\n', repl=' ', string=article['content']).replace('  ', ' ')
            for word in text.split(' '):
                if not word or word == ' ':
                    continue
                processed_word = morph.parse(re.sub(pattern=r'[,!?\.«»\n]', repl='', string=word))[0]
                if processed_word.tag.POS not in ('NOUN', 'ADJF', 'ADJS', 'VERB', 'INFN'):
                    continue

                norm_form = processed_word.normal_form
                if not result.get(norm_form):
                    result[norm_form] = 0
                result[norm_form] += 1

        # сортировка по значению
        result = dict(reversed(sorted(result.items(), key=lambda item: item[1])))
        # обрезка по лимиту
        result = dict(islice(result.items(), args.get('limit')))
        return result, 200
