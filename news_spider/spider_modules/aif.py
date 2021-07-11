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


def aif_parser():
    print(f'aif job started at {datetime.datetime.now()}')
    page = 1
    while True:
        r = requests.post(f'https://aif.ru/moscow', data={'page': page})
        if r.status_code != 200:
            print(
                f'aif job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find_all('div', {'class': 'list_item'})
        for news in news_list:
            try:
                news_url = news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'aif job ended at {datetime.datetime.now()}')
                    return
                str_time = news.find('span', {'class': 'text_box__date'}).text
                dt_now = datetime.datetime.now()
                time_data = {
                    'hour': int(str_time[:2]),
                    'minute': int(str_time[-2:]),
                    'second': 0,
                    'microsecond': 0,
                }
                if re.findall(r'^\d{2}:\d{2}$', str_time):
                    time_data['year'] = dt_now.year
                    time_data['month'] = dt_now.month
                    time_data['day'] = dt_now.day
                elif re.findall(r'^\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}$', str_time):
                    time_data['year'] = int(str_time[6:10])
                    time_data['month'] = int(str_time[3:5])
                    time_data['day'] = int(str_time[:2])
                news_dt = datetime.datetime(**time_data)
                if news_dt < dt_now - datetime.timedelta(**config.tracked_time):
                    print(f'aif job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru', config=config.newspaper_config)
                article.download()
                article.parse()
                data = {
                    'source': 'aif',
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
    aif_parser()
