import datetime
import logging
import re
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col


def bfm_parser():
    print(f'bfm job started at {datetime.datetime.now()}')
    page = 1
    while True:
        url = 'https://www.bfm.ru/news'
        params = {'type': 'news', 'page': page}
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(
                f'bfm job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('section', {'class': 'search-list'}).find_all('li')
        for news in news_list:
            try:
                news_url = 'https://www.bfm.ru' + news.find('a', {'class': 'title-link'}).get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'bfm job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                r = requests.get(news_url)
                if r.status_code != 200:
                    print(
                        f'm24 job error, request status code != 200\n'
                        f'url: {r.url}\n'
                        f'status code: {r.status_code}\n'
                        f'at {datetime.datetime.now()}'
                    )
                    return
                soup = BeautifulSoup(r.text, 'lxml')
                str_time = soup.find('span', {'class': 'date'}).contents[0][2:-2]
                month = ['января', 'февраля', 'марта', "апреля", "мая", "июня", "июля", "августа", "сентября",
                         "октября", "ноября", "декабря"]
                news_month = re.search(r'[а-яА-Я]+', str_time).group()
                time_data = {
                    'year': int(str_time[-11:-7]),
                    'month': month.index(news_month) + 1,
                    'day': int(str_time[:2] if str_time[:2].isdigit() else str_time[:1]),
                    'hour': int(str_time[-5:-3]),
                    'minute': int(str_time[-2:]),
                    'second': 0,
                    'microsecond': 0
                }
                news_dt = datetime.datetime(**time_data)
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'm24 job ended at {datetime.datetime.now()}')
                    return
                article.set_html(r.text)
                article.parse()
                data = {
                    'source': 'bfm',
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
        page += 1


if __name__ == '__main__':
    bfm_parser()
