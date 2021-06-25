import datetime
import logging
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def tvrain_parser():
    print(f'tvrain job started at {datetime.datetime.now()}')
    page = 1
    while True:
        r = requests.get('https://tvrain.ru/news', params={'page': page})
        if r.status_code != 200:
            print(
                f'tvrain job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('div', {'class': 'newsline__block'}).find_all('div', {'class': 'newsline__row'})
        for news in news_list:
            try:
                link_tag = news.find('a')
                if link_tag:
                    news_url = 'https://tvrain.ru' + link_tag.get('href')
                else:
                    continue

                if news_db_col.find_one({'url': news_url}):
                    print(f'tvrain job ended at {datetime.datetime.now()}')
                    return
                r = requests.get(news_url)
                if r.status_code != 200:
                    print(
                        f'tvrain job error, request status code != 200\n'
                        f'url: {r.url}\n'
                        f'status code: {r.status_code}\n'
                        f'at {datetime.datetime.now()}'
                    )
                    return
                soup = BeautifulSoup(r.text, 'lxml')
                news_dt_str = soup.find('span', {'class': 'document-head__date'}).text[5:-3]
                month = ['января', 'февраля', 'мартa', "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
                news_dt = datetime.datetime(**{
                    'year': datetime.datetime.now().year,
                    'month': month.index(news_dt_str[3:-7])+1,
                    'day': int(news_dt_str[:2]),
                    'hour': int(news_dt_str[-5:-3]),
                    'minute': int(news_dt_str[-2:]),
                    'second': 0,
                    'microsecond': 0,
                })
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'tvrain job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.set_html(r.text)
                article.parse()
                data = {
                    'source': 'tvrain',
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
    tvrain_parser()
