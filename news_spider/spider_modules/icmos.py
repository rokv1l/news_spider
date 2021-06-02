import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

from src.database import news_db_col


def icmos_parser():
    print(f'icmos job started at {datetime.datetime.now()}')
    page = 1
    while True:
        r = requests.get('https://icmos.ru/news', params={'page': page})
        if r.status_code != 200:
            print(f'm24 job ended at {datetime.datetime.now()}')
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('div', {'class': 'multimedia_other'}).find_all('div', {'class': 'big'})
        for news in news_list:
            news_url = 'https://icmos.ru' + news.find('a').get('href')
            if news_db_col.find_one({'url': news_url}):
                print(f'icmos job ended at {datetime.datetime.now()}')
                return
            r = requests.get(news_url)
            if r.status_code != 200:
                print(f'm24 job ended at {datetime.datetime.now()}')
                return
            soup = BeautifulSoup(r.text, 'lxml')
            news_dt_str = soup.find('div', {'class': 'path clearfix'}).find('div', {'class': 'right'}).text.replace(' ', '')
            month = ['января', 'февраля', 'марта', "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
            news_dt = datetime.datetime(**{
                'year': int(news_dt_str[7:11]),
                'month': month.index(news_dt_str[3:7])+1,
                'day': int(news_dt_str[1:3]),
                'hour': int(news_dt_str[-6:-4]),
                'minute': int(news_dt_str[-2:]),
                'second': 0,
                'microsecond': 0,
            })
            if news_dt < datetime.datetime.now() - datetime.timedelta(days=30):
                print(f'icmos job ended at {datetime.datetime.now()}')
                return
            article = Article(news_url, language='ru')
            try:
                article.set_html(r.text)
                article.parse()
            except Exception:
                continue
            data = {
                'source': 'icmos',
                'url': news_url,
                'title': article.title,
                'content': article.text,
                'datetime': news_dt
            }
            news_db_col.insert_one(data)
            sleep(1)
        page += 1


if __name__ == '__main__':
    icmos_parser()