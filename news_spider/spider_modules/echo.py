import datetime
import logging
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def echo_parser():
    print(f'echo job started at {datetime.datetime.now()}')
    search_dt = datetime.datetime.now().date()
    while True:
        r = requests.get(f'https://echo.msk.ru/news/{search_dt.year}/{search_dt.month}/{search_dt.day}/')
        if r.status_code != 200:
            print(
                f'echo job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('div', {'class': 'newslist'}).find_all('div', {'class': 'newsblock'})
        news_list.reverse()
        for news in news_list:
            try:
                news_url = 'https://echo.msk.ru' + news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'echo job ended at {datetime.datetime.now()}')
                    return
                news_time_str = news.find('span', {'class': 'datetime'}).text
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
                    print(f'echo job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'echo',
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
        search_dt = search_dt - datetime.timedelta(days=1)


if __name__ == '__main__':
    echo_parser()
