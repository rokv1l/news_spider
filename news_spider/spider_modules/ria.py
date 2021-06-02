import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col


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
            article = Article(news_url, language='ru')
            try:
                article.set_html(r.text)
                article.parse()
            except Exception:
                continue
            data = {
                'source': 'ria',
                'url': news_url,
                'title': article.title,
                'content': article.text,
                'datetime': news_dt
            }
            print(data)
            news_db_col.insert_one(data)
            params['id'] = soup.find('meta', {'name': 'relap-entity-id'}).get('content')
            params['date'] = f'{news_dt.year}{news_dt.month}{news_dt.day}T{news_dt.hour}{news_dt.minute}{news_dt.second}'
            sleep(config.request_delay)


if __name__ == '__main__':
    ria_parser()
