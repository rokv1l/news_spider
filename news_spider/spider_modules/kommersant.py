import datetime
import logging
import json
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
# from src.database import news_db_col


def kommersant_parser():
    print(f'kommersant job started at {datetime.datetime.now()}')
    limit = 16
    offset = 0
    while True:
        url = 'https://www.kommersant.ru/theme/storydocs'
        params = {
            'id': '3378',
            'pageSize': limit,
            'offset': offset,
        }
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(
                f'kommersant job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        data = r.json()
        if not data.get('data'):
            return
        for article in data.get('data'):
            try:
                news_url = f'https://www.kommersant.ru/doc/{article["id"]}'
                # if news_db_col.find_one({'url': news_url}):
                #     print(f'kommersant job ended at {datetime.datetime.now()}')
                #     return
                r = requests.get(news_url)
                if r.status_code != 200:
                    print(
                        f'kommersant job error, request status code != 200\n'
                        f'url: {r.url}\n'
                        f'status code: {r.status_code}\n'
                        f'at {datetime.datetime.now()}'
                    )
                    return
                soup = BeautifulSoup(r.text, 'lxml')
                news_dt_tag = soup.find('meta', {'itemprop': 'datePublished'})
                if not news_dt_tag:
                    continue
                news_dt_str = news_dt_tag.get('content')
                news_dt = datetime.datetime.fromisoformat(news_dt_str[:-6])
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'kommersant job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.set_html(r.text)
                article.parse()
                data = {
                    'source': 'kommersant',
                    'url': news_url,
                    'title': article.title,
                    'content': article.text,
                    'datetime': news_dt.isoformat()
                }
                print(news_url)
                # news_db_col.insert_one(data)
            except Exception as e:
                print(f'Warning: Error in job')
                traceback.print_exc()
                continue
            sleep(config.request_delay)
        offset += limit


if __name__ == '__main__':
    kommersant_parser()
