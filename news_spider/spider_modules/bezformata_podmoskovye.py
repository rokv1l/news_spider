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


def bezformata_podmoskovye_parser():
    print(f'bezformata_podmoskovye job started at {datetime.datetime.now()}')
    page = 1
    while True:
        url = 'https://podmoskovye.bezformata.com/daynews/'
        dt_now = datetime.datetime.now()
        params = {
            'npage': page,
            'nday': dt_now.day,
            'nmonth': dt_now.month,
            'nyear': dt_now.year,
        }
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(
                f'bezformata_podmoskovye job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_data = soup.find('section', {'class': 'listtopicbox'})
        if not news_data:
            print(f'bezformata_podmoskovye job ended at {datetime.datetime.now()}')
            return
        news_list = news_data.find_all('article', {'class': 'listtopicline'})
        for news in news_list:
            try:
                news_url = news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'bezformata_podmoskovye job ended at {datetime.datetime.now()}')
                    return
                r = requests.get(news_url)
                soup = BeautifulSoup(r.text, 'lxml')
                str_time = soup.find('div', {'class': 'sourcedatebox'}).find('span').get('title')[:16]
                news_dt = datetime.datetime.strptime(str_time, '%d.%m.%Y %H:%M')

                if news_dt < dt_now - datetime.timedelta(**config.tracked_time):
                    print(f'bezformata_podmoskovye job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.set_html(r.text)
                article.parse()
                data = {
                    'source': 'bezformata_podmoskovye',
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
    bezformata_podmoskovye_parser()
