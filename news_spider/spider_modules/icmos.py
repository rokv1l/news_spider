import datetime
import logging
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def icmos_parser():
    print(f'icmos job started at {datetime.datetime.now()}')
    page = 1
    while True:
        r = requests.get('https://icmos.ru/news', params={'page': page})
        if r.status_code != 200:
            print(
                f'icmos job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('div', {'class': 'multimedia_other'}).find_all('div', {'class': 'big'})
        for news in news_list:
            try:
                news_url = 'https://icmos.ru' + news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'icmos job ended at {datetime.datetime.now()}')
                    return
                r = requests.get(news_url)
                if r.status_code != 200:
                    print(
                        f'icmos job error, request status code != 200\n'
                        f'url: {r.url}\n'
                        f'status code: {r.status_code}\n'
                        f'at {datetime.datetime.now()}'
                    )
                    return
                soup = BeautifulSoup(r.text, 'lxml')
                news_dt_str = soup.find('div', {'class': 'news-title'}).find('span').text
                month = ['января', 'февраля', 'мартa', "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
                news_dt = datetime.datetime(**{
                    'year': int(news_dt_str[-4:]),
                    'month': month.index(news_dt_str[3:-5])+1,
                    'day': int(news_dt_str[:2]),
                    'hour': 0,
                    'minute': 0,
                    'second': 0,
                    'microsecond': 0,
                })
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'icmos job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.set_html(r.text)
                article.parse()
                data = {
                    'source': 'icmos',
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
                continue
            sleep(config.request_delay)
        page += 1


if __name__ == '__main__':
    icmos_parser()
