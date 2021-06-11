import re
import datetime
from time import sleep

import requests
from newspaper import Article
from bs4 import BeautifulSoup

import config
from src.database import news_db_col


def lenta_parser():
    print(f'lenta job started at {datetime.datetime.now()}')
    url = 'https://lenta.ru/rubrics/russia/moscow/'
    r = requests.get(url)
    if r.status_code != 200:
        print(
            f'lenta job error, request status code != 200\n'
            f'url: {r.url}\n'
            f'status code: {r.status_code}\n'
            f'at {datetime.datetime.now()}'
        )
        return
    soup = BeautifulSoup(r.text, 'lxml')
    news_list = soup.find_all('div', {'class': 'news'})
    news_list = [news for news in news_list if news.find('span', {'class': 'time'})]
    for news in news_list:
        try:
            dt_now = datetime.datetime.now()
            str_time = news.find('span', {'class': 'time'}).text
            news_dt = datetime.datetime(
                year=dt_now.year,
                month=dt_now.month,
                day=dt_now.day,
                hour=int(str_time[:2]),
                minute=int(str_time[3:]),
                second=0,
                microsecond=0
            )
            news_url = news.find('a').get('href')
            if not re.match(r'^https', news_url):
                news_url = 'https://lenta.ru' + news_url
            if news_db_col.find_one({'url': news_url}):
                print(f'lenta job ended at {datetime.datetime.now()}')
                continue
            news = Article(news_url, language='ru')
            news.download()
            news.parse()
            data = {
                'source': 'lenta',
                'url': news_url,
                'title': news.title,
                'content': news.text,
                'datetime': news_dt.isoformat()
            }
            print(news_url)
            news_db_col.insert_one(data)
            sleep(config.request_delay)
        except Exception as e:
            print(f'Warning: error when processing news - {e}')
            continue


if __name__ == '__main__':
    lenta_parser()
