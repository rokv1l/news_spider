# Писал Лёнин соколёнок

import datetime
import traceback
import re
from time import sleep

import requests
import json
from bs4 import BeautifulSoup
from newspaper import Article

import config

from src.database import news_db_col, errors_db_col


def mn_parser():
    print(f'mn job started at {datetime.datetime.now()}')
    page = 1
    while True:
        params = {
            'page': page,
            'page_size': 10,
        }
        url = 'https://www.mn.ru/api/v1/articles/more'
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(
                f'mn job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        api_dict = r.json()
        for news in api_dict['data']:
            try:
                news_url = news['attributes']['url']
                if news_db_col.find_one({'url': news_url}):
                    print(f'mn job ended at {datetime.datetime.now()}')
                    return
                dt_now = datetime.datetime.now()
                news_dt = datetime.datetime.fromisoformat(news['attributes']['published_at'].split('.')[0])

                if news_dt < dt_now - datetime.timedelta(**config.tracked_time):
                    print(f'mn job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru', config=config.newspaper_config)
                article.download()
                article.parse()
                data = {
                    'source': 'mn',
                    'url': news_url,
                    'title': article.title,
                    'content': article.text,
                    'datetime': news_dt.isoformat()
                }
                print(news_url)
                news_db_col.insert_one(data)

            except Exception as e:
                print(e)
                traceback.print_exc()
                errors_db_col.insert_one({
                    'error': str(traceback.format_exc()),
                    'checked': False,
                    'timestamp': datetime.datetime.now().timestamp()
                })
                sleep(10)
                continue
            sleep(config.request_delay)
        page += 1


if __name__ == '__main__':
    mn_parser()
