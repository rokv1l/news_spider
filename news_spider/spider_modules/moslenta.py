import datetime
import logging
import traceback
from time import sleep

import requests
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def moslenta_parser():
    print(f'moslenta job started at {datetime.datetime.now()}')
    limit = 100
    offset = 0
    while True:
        url = 'https://moslenta.ru/api/v2/topics'
        params = {
            'limit': limit,
            'offset': offset,
        }
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(
                f'moslenta job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        data = r.json()
        if not data.get('data'):
            # что то не так
            return
        for article in data.get('data'):
            try:
                news_dt = datetime.datetime.fromisoformat(article['attributes']['published_at'][:-5])
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'moslenta job ended at {datetime.datetime.now()}')
                    return
                news_url = f'https://moslenta.ru{article["attributes"]["link"]}'
                if news_db_col.find_one({'url': news_url}):
                    print(f'moslenta job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'moslenta',
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
                continue
            sleep(config.request_delay)
        offset += limit


if __name__ == '__main__':
    moslenta_parser()
