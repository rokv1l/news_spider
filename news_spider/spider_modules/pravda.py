import datetime
import logging
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col


def pravda_parser():
    print(f'pravda job started at {datetime.datetime.now()}')
    search_dt = datetime.datetime.now().date()
    while True:
        search_dt_str = f'{search_dt.year}-' \
                        f'{search_dt.month if search_dt.month > 9 else f"0{search_dt.month}"}-' \
                        f'{search_dt.day if search_dt.day > 9 else f"0{search_dt.day}"}'
        r = requests.get(f'https://www.pravda.ru/archive/{search_dt_str}/')
        if r.status_code != 200:
            print(
                f'pravda job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('div', {'class': 'news block'}).find_all('div', {'class': 'article'})
        news_list.reverse()
        for news in news_list:
            try:
                news_url = news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'pravda job ended at {datetime.datetime.now()}')
                    return
                news_dt_str = news.find('time').get('datetime')
                news_dt = datetime.datetime.fromisoformat(news_dt_str[:-1])
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'pravda job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'pravda',
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
                continue
            sleep(config.request_delay)
        search_dt = search_dt - datetime.timedelta(days=1)


if __name__ == '__main__':
    pravda_parser()
