import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col


def mockva_parser():
    print(f'mockva job started at {datetime.datetime.now()}')
    page = 1
    while True:
        r = requests.get(f'https://mockva.ru/category/gorod/page/{page}')
        if r.status_code != 200:
            print(
                f'icmos job error, request status code != 200\n'
                f'mockva: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find_all('div', {'class': 'post-card__body'})
        for news in news_list:
            try:
                news_dt_str = news.find('time').text
                news_dt = datetime.datetime(**{
                    'year': int(news_dt_str[6:10]),
                    'month': int(news_dt_str[3:5]),
                    'day': int(news_dt_str[:2]),
                    'hour': int(news_dt_str[-5:-3]),
                    'minute': int(news_dt_str[-2:]),
                    'second': 0,
                    'microsecond': 0,
                })
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'mockva job ended at {datetime.datetime.now()}')
                    return
                news_url = news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'mockva job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'mockva',
                    'url': news_url,
                    'title': article.title,
                    'content': article.text,
                    'datetime': news_dt.isoformat()
                }
                news_db_col.insert_one(data)
                sleep(config.request_delay)
            except Exception:
                continue
        page += 1


if __name__ == '__main__':
    mockva_parser()
