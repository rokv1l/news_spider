import datetime
import logging
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def ria_parser():
    print(f'ria job started at {datetime.datetime.now()}')
    params = {}
    while True:
        r = requests.get('https://ria.ru/services/location_Moskva/more.html', params=params)
        if r.status_code != 200:
            print(
                f'ria job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find_all('div', {'class': 'list-item'})
        for news in news_list:
            try:
                news_url = news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'ria job ended at {datetime.datetime.now()}')
                    return
                r = requests.get(news_url)
                if r.status_code != 200:
                    print(
                        f'ria job error, request status code != 200\n'
                        f'url: {r.url}\n'
                        f'status code: {r.status_code}\n'
                        f'at {datetime.datetime.now()}'
                    )
                    return
                soup = BeautifulSoup(r.text, 'lxml')
                news_dt_str = soup.find('div', {'class': 'article__info-date'}).find('a').text
                news_dt = datetime.datetime(**{
                    'year': int(news_dt_str[-4:]),
                    'month': int(news_dt_str[-7:-5]),
                    'day': int(news_dt_str[6:8]),
                    'hour': int(news_dt_str[:2]),
                    'minute': int(news_dt_str[3:5]),
                    'second': 0,
                    'microsecond': 0,
                })
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'ria job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru', config=config.newspaper_config)
                article.set_html(r.text)
                article.parse()
                data = {
                    'source': 'ria',
                    'url': news_url,
                    'title': article.title,
                    'content': article.text,
                    'datetime': news_dt.isoformat()
                }
                print(news_url)
                news_db_col.insert_one(data)
                params['id'] = soup.find('meta', {'name': 'relap-entity-id'}).get('content')
                params['date'] = f'{news_dt.year}' \
                                 f'{news_dt.month if news_dt.month > 9 else f"0{news_dt.month}"}' \
                                 f'{news_dt.day if news_dt.day > 9 else f"0{news_dt.day}"}T' \
                                 f'{news_dt.hour if news_dt.hour > 9 else f"0{news_dt.hour}"}' \
                                 f'{news_dt.minute if news_dt.minute > 9 else f"0{news_dt.minute}"}' \
                                 f'00'
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


if __name__ == '__main__':
    ria_parser()
