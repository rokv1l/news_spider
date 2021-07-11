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


def msknovosti_parser():
    print(f'msknovosti job started at {datetime.datetime.now()}')
    r = requests.get(f'https://msknovosti.ru/all-news/')
    if r.status_code != 200:
        print(
            f'msknovosti job error, request status code != 200\n'
            f'url: {r.url}\n'
            f'status code: {r.status_code}\n'
            f'at {datetime.datetime.now()}'
        )
        return
    soup = BeautifulSoup(r.text, 'lxml')
    news_list = soup.find_all('div', {'class': 'rt-equal-height'})
    today = datetime.datetime.now().date()
    for news in news_list:
        try:
            news_url = news.find('a').get('href')
            if news_db_col.find_one({'url': news_url}):
                print(f'msknovosti job ended at {datetime.datetime.now()}')
                return
            news_dt_str = news.find('span', {'class': 'date'}).text
            if 'Сегодня' in news_dt_str:
                news_dt_str = news_dt_str.replace('Сегодня в ', f"{today.isoformat()}T")
                news_dt = datetime.datetime.fromisoformat(news_dt_str)
            elif 'Вчера' in news_dt_str:
                yesterday = today - datetime.timedelta(days=1)
                news_dt_str = news_dt_str.replace('Вчера в ', f"{yesterday.isoformat()}T")
                news_dt = datetime.datetime.fromisoformat(news_dt_str)
            else:
                news_dt = datetime.datetime.strptime(f'{news_dt_str} 00:00', '%d.%m.%Y %H:%M')
            if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                print(f'msknovosti job ended at {datetime.datetime.now()}')
                return
            article = Article(news_url, language='ru')
            article.download()
            article.parse()
            data = {
                'source': 'msknovosti',
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


if __name__ == '__main__':
    msknovosti_parser()
