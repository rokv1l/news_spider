import datetime
import logging
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col


def interfax_parser():
    print(f'interfax job started at {datetime.datetime.now()}')
    search_dt = datetime.datetime.now().date()

    while True:
        r = requests.get(
            f'https://www.interfax.ru/moscow/news/'
            f'{search_dt.year}/'
            f'{search_dt.month if search_dt.month > 9 else f"0{search_dt.month}"}/'
            f'{search_dt.day if search_dt.day > 9 else f"0{search_dt.day}"}'
        )
        if r.status_code != 200:
            print(
                f'interfax job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('div', {'class': 'an'}).find_all('div')
        for news in news_list:
            if not news.get('data-id'):
                continue
            try:
                news_url = 'https://www.interfax.ru' + news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'interfax job ended at {datetime.datetime.now()}')
                    return
                news_time_str = news.find('span').text
                news_dt = datetime.datetime(**{
                    'year': search_dt.year,
                    'month': search_dt.month,
                    'day': search_dt.day,
                    'hour': int(news_time_str[:2]),
                    'minute': int(news_time_str[-2:]),
                    'second': 0,
                    'microsecond': 0,
                })
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'interfax job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'interfax',
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
                continue
            sleep(config.request_delay)
        search_dt = search_dt - datetime.timedelta(days=1)


if __name__ == '__main__':
    interfax_parser()
