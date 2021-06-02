import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col


def vm_parser():
    print(f'vm job started at {datetime.datetime.now()}')
    page = 1
    while True:
        url = 'https://vm.ru/listing/602f9dccea8b287bb9d8727d/news.html'
        params = {'page': page, 'limit': 40}
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(
                f'vm job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('div', {'class': 'listing news-listing'}).find_all('article')
        for news in news_list:
            news_url = 'https://vm.ru' + news.find('a').get('href')
            if news_db_col.find_one({'url': news_url}):
                print(f'vm job ended at {datetime.datetime.now()}')
                return
            r = requests.get(news_url)
            if r.status_code != 200:
                print(
                    f'vm job error, request status code != 200\n'
                    f'url: {r.url}\n'
                    f'status code: {r.status_code}\n'
                    f'at {datetime.datetime.now()}'
                )
                return
            soup = BeautifulSoup(r.text, 'lxml')
            str_time = soup.find('time', {'class': 'article-time'}).text
            dt_now = datetime.datetime.now()
            month = ['января', 'февраля', 'марта', "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
            news_dt = datetime.datetime(
                year=dt_now.year,
                month=month.index(str_time[3:-6]) + 1,
                day=int(str_time[:2]),
                hour=int(str_time[-5:-3]),
                minute=int(str_time[-2:]),
                second=0,
                microsecond=0
            )
            if news_dt < dt_now - datetime.timedelta(**config.tracked_time):
                print(f'vm job ended at {datetime.datetime.now()}')
                return
            article = Article(news_url, language='ru')
            try:
                article.set_html(r.text)
                article.parse()
            except Exception:
                continue
            if article.publish_date < datetime.datetime.now() - datetime.timedelta(days=30):
                print(f'vm job ended at {datetime.datetime.now()}')
                return
            data = {
                'source': 'vm',
                'url': news_url,
                'title': article.title,
                'content': article.text,
                'datetime': news_dt
            }
            print(data)
            news_db_col.insert_one(data)
            sleep(config.request_delay)
        page += 1


if __name__ == '__main__':
    vm_parser()
