import re
import datetime
from time import sleep

import requests
from newspaper import Article
from bs4 import BeautifulSoup

import config
from src.database import news_db_col


def rt_parser():
    print(f'rt job started at {datetime.datetime.now()}')
    limit = 10
    page = 1
    while True:
        url = f'https://russian.rt.com/listing/tag.moskva/prepare/all-new/{limit}/{page}'
        r = requests.get(url)
        if r.status_code != 200:
            print(
                f'rt job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('ul', {'class': 'listing__rows'}).find_all('li', {'class': 'listing__column_all-new'})
        for news in news_list:
            try:
                str_time = news.find('time', {'class': 'date'}).get('datetime')
                try:
                    news_dt = datetime.datetime.fromisoformat(str_time.replace(' ', 'T') + ':00')
                except ValueError:
                    str_time = str_time[:8] + '0' + str_time[8:]
                    news_dt = datetime.datetime.fromisoformat(str_time.replace(' ', 'T') + ':00')
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'rt job ended at {datetime.datetime.now()}')
                    return
                news_url = f'https://russian.rt.com{news.find("a", {"class": "link"}).get("href")}'
                if news_db_col.find_one({'url': news_url}):
                    print(f'rt job ended at {datetime.datetime.now()}')
                    return
                news = Article(news_url, language='ru')
                news.download()
                news.parse()
                data = {
                    'source': 'rt',
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
        page += 1


if __name__ == '__main__':
    rt_parser()
