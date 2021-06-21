import datetime
import logging
import traceback
import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def mbk_parser():
    print(f'mbk job started at {datetime.datetime.now()}')
    page = 1
    while True:
        r = requests.get(f'https://mbk-news.appspot.com/category/news/page/{page}/')
        if r.status_code != 200:
            print(
                f'mbk job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('ul', {'class': 'g1-collection-items'}).find_all('li', {'class': 'g1-collection-item'})
        for news in news_list:
            try:
                news_url = news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'mbk job ended at {datetime.datetime.now()}')
                    return
                str_time = news.find('time', {'class': 'entry-date'}).get('datetime')[:-6]
                news_dt = datetime.datetime.fromisoformat(str_time)
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'mbk job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'mbk',
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
        page += 1


if __name__ == '__main__':
    mbk_parser()
