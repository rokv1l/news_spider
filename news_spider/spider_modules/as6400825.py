import datetime
import logging
import re
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def as6400825_parser():
    print(f'as6400825 job started at {datetime.datetime.now()}')
    page = 1
    while True:
        url = f'https://as6400825.ru/page/{page}'
        r = requests.get(url)
        if r.status_code != 200:
            print(
                f'as6400825 job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find_all('article', {'class': 'listing-item-blog'})
        for news in news_list:
            try:
                news_url = news.find('a', {'class': 'img-holder'}).get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'as6400825 job ended at {datetime.datetime.now()}')
                    return
                str_time = soup.find('time', {'class': 'post-published'}).get('datetime')[:-6]
                news_dt = datetime.datetime.fromisoformat(str_time)
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'as6400825 job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'as6400825',
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
        page += 1


if __name__ == '__main__':
    as6400825_parser()
