# Писал Лёнин соколёнок

import datetime
import traceback
import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def inregiontoday_parser():
    print(f'inregiontoday job started at {datetime.datetime.now()}')
    page = 1
    while True:
        url = 'https://msk.inregiontoday.ru/'
        params = {
            'cat': 1,
            'paged': page,
        }
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(
                f'inregiontoday job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find_all('article', {'class': 'post'})
        months = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
        for news in news_list:
            try:
                news_url = news.find('h2').find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'inregiontoday job ended at {datetime.datetime.now()}')
                    return
                str_time = news.find('p').text.split('.')[0]
                if '–' in str_time:
                    str_time = str_time.split('–')[1][1:].split(" ")
                elif ',' in str_time:
                    if len(str_time) <= 3:
                        str_time = str_time.split(',')[1][1:].split(" ")
                        str_time[1] = str_time[1][:-1]
                    else:
                        continue

                dt_now = datetime.datetime.now()
                time_data = {
                    'year': dt_now.year,
                    'month': months.index(str_time[1]) + 1,
                    'day': int(str_time[0]),
                    'hour': 0,
                    'minute': 0,
                    'second': 0,
                    'microsecond': 0,
                }

                if len(str_time) == 3:
                    time_data.update({'year': str_time[2]})

                news_dt = datetime.datetime(**time_data)
                if news_dt < dt_now - datetime.timedelta(**config.tracked_time):
                    print(f'inregiontoday job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'inregiontoday',
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
    inregiontoday_parser()
