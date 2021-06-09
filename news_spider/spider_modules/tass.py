import datetime
from time import sleep

import requests
from newspaper import Article

import config
from src.database import news_db_col


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
                news_url = f'https://tass.ru/moskva/{article[0]["id"]}'
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
                news_db_col.insert_one(data)
                sleep(config.request_delay)
            except Exception:
                continue
        offset += limit


if __name__ == '__main__':
    tass_parser()
