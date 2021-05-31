import datetime
from time import sleep

import requests
from newspaper import Article

from src.database import news_db_col


def tass_parser():
    print(f'tass job started at {datetime.datetime.now()}')
    limit = 100
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
        data = requests.get(url, params=params).json()
        if not data.get('data') or not data.get('data').get('news'):
            return
        for article in data.get('data').get('news'):
            news_dt = datetime.datetime.fromtimestamp(article[0]['publishDate'])
            if news_dt < datetime.datetime.now() - datetime.timedelta(days=30):
                print(f'tass job ended at {datetime.datetime.now()}')
                return
            news_url = f'https://tass.ru/moskva/{article[0]["id"]}'
            if news_db_col.find_one({'url': news_url}):
                print(f'tass job ended at {datetime.datetime.now()}')
                return
            else:
                article = Article(news_url, language='ru')
                try:
                    article.download()
                    article.parse()
                except Exception:
                    continue
                data = {
                    'source': 'tass',
                    'url': news_url,
                    'title': article.title,
                    'content': article.text,
                    'datetime': news_dt
                }
                news_db_col.insert_one(data)
        offset += limit
        sleep(1)


if __name__ == '__main__':
    tass_parser()
