import datetime
import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col


def m24_parser():
    print(f'm24 job started at {datetime.datetime.now()}')
    page = 1
    while True:
        url = 'https://www.m24.ru/news'
        params = {
            'page': page,
            'ajax': 1
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }
        r = requests.get(url, params=params, headers=headers)
        if r.status_code != 200:
            print(
                f'm24 job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        data = r.json()
        for article in data['materials']:
            news_url = f'https://m24.ru{article.get("url")}'
            if news_db_col.find_one({'url': news_url}):
                print(f'm24 job ended at {datetime.datetime.now()}')
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
            dt_now = datetime.datetime.now()
            str_time = soup.find('p', {'class': 'b-material__date'}).text
            time_data = {
                'year': dt_now.year,
                'second': 0,
                'microsecond': 0,
                'hour': int(str_time[-5:-3]),
                'minute': int(str_time[-2:]),
            }
            if re.findall(r'\d\d:\d\d', str_time):
                time_data['month'] = dt_now.month
                time_data['day'] = dt_now.day
            elif re.findall(r'\d{1,2}\s\w+\s\d\d:\d\d', str_time):
                month = ['января', 'февраля', 'марта', "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
                time_data['month'] = month.index(str_time[3:-7]) + 1
                time_data['day'] = int(str_time[:2])

            news_dt = datetime.datetime(**time_data)
            if news_dt < dt_now - datetime.timedelta(**config.tracked_time):
                print(f'm24 job ended at {datetime.datetime.now()}')
                return
            try:
                article.set_html(r.text)
                article.parse()
            except Exception:
                continue
            data = {
                'source': 'm24',
                'url': news_url,
                'title': article.title,
                'content': article.text,
                'datetime': news_dt
            }
            news_db_col.insert_one(data)
            sleep(config.request_delay)
        page += 1


if __name__ == '__main__':
    m24_parser()
