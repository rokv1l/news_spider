# Писал Лёнин соколёнок

import datetime
import traceback
import re
from time import sleep

import requests
import json
from bs4 import BeautifulSoup
from newspaper import Article
from newspaper import ArticleException

import config

from src.database import news_db_col, errors_db_col


def mperspektiva_parser():
    print(f'mperspektiva job started at {datetime.datetime.now()}')
    page = 1
    months = ['января', 'февраля ', 'марта ', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября',
              'ноября', 'декабря']
    month = None
    while True:
        params = {
            'PAGEN_1': page,
            'ajax': 'Y',
        }
        url = 'https://mperspektiva.ru/news/'
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(
                f'mperspektiva job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find_all('div', {'class': 'c-articles-grid__content'})
        count = 0
        for news in news_list:
            try:
                news_url = "http://mperspektiva.ru" + news.find_parent('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'molnet job ended at {datetime.datetime.now()}')
                    return
                pretime = news.find('span', {'class': 'date'}).text.split(" ")
                predate = news.find('span', {'class': 'time'}).text
                if int(pretime[0]) < 10:
                    pretime[0] = "0" + pretime[0]
                if int(months.index(pretime[1].lower())) < 10:
                    month = "0" + str(months.index(pretime[1].lower()) + 1)
                str_time = f"{str(pretime[2])}-{str(month)}-{pretime[0]} {predate}"

                dt_now = datetime.datetime.now()
                time_data = {
                    'hour': 0,
                    'minute': 0,
                    'second': 0,
                    'microsecond': 0,
                }

                if re.findall(r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}$', str_time):
                    time_data.update({'year': int(str_time[:4])})
                    time_data.update({'month': int(str_time[5:7])})
                    time_data.update({'day': int(str_time[8:10])})
                    time_data.update({'hour': int(str_time[11:13])})
                    time_data.update({'minute': int(str_time[14:16])})
                else:
                    time_data.update({'year': dt_now.year})
                    time_data.update({'month': dt_now.month})
                    time_data.update({'day': dt_now.day})

                news_dt = datetime.datetime(**time_data)
                if news_dt < dt_now - datetime.timedelta(**config.tracked_time):
                    print(f'mperspektiva job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru', config=config.newspaper_config)
                try:
                    article.download()
                    article.parse()
                except ArticleException:
                    continue
                article.parse()
                data = {
                    'source': 'mperspektiva',
                    'url': news_url,
                    'title': article.title,
                    'content': article.text,
                    'datetime': news_dt.isoformat()
                }

                count += 1
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
    mperspektiva_parser()
