import datetime
import logging
import json
import traceback
from time import sleep

import requests
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def tass_parser():
    print(f'tass job started at {datetime.datetime.now()}')
    limit = 20
    offset = 0
    while True:
        url = 'https://tass.ru/rubric/api/v1/rubric-articles'
        params = {
            'slug': 'moskva',
            'type': 'all',
            'step': 'NaN',
            'tuplesLimit': limit,
            'newsOffset': offset,
        }
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(
                f'tass job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        data = r.json()
        if not data.get('data') or not data.get('data').get('news'):
            # что то не так
            return
        for article in data.get('data').get('news'):
            try:
                news_dt = datetime.datetime.fromtimestamp(article[0]['publishDate'])
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'tass job ended at {datetime.datetime.now()}')
                    return
                news_url = f'https://tass.ru/{article[0]["slug"]}/{article[0]["id"]}'
                if news_db_col.find_one({'url': news_url}):
                    print(f'tass job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'tass',
                    'url': news_url,
                    'title': article.title,
                    'content': article.text,
                    'datetime': news_dt.isoformat()
                }
                print(news_url)
                news_db_col.insert_one(data)
            except Exception as e:
                print(f'Warning: Error in job')
                traceback.print_exc()
                errors_db_col.insert_one({
                    'error': str(traceback.format_exc()),
                    'checked': False,
                    'timestamp': datetime.datetime.now().timestamp()
                })
                sleep(10)
                continue
            sleep(config.request_delay)
        offset += limit


if __name__ == '__main__':
    tass_parser()
