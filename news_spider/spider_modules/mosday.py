import datetime
import logging
import re
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def mosday_parser():
    print(f'mosday job started at {datetime.datetime.now()}')
    search_dt = datetime.datetime.now().date()
    while True:
        search_dt_str = f'{search_dt.year}' \
                        f'{search_dt.month if search_dt.month > 9 else f"0{search_dt.month}"}' \
                        f'{search_dt.day if search_dt.day > 9 else f"0{search_dt.day}"}'
        r = requests.get(f'http://mosday.ru/news/date.php?{search_dt_str}&sort=pub')
        if r.status_code != 200:
            print(
                f'mosday job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find_all('table')[11].find_all('tr')
        for news in news_list:
            try:
                news_url = 'http://mosday.ru/news/' + news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'mosday job ended at {datetime.datetime.now()}')
                    return
                news_time_str = news.find('td').text[:5]
                if not re.search(r'\d\d:\d\d', news_time_str):
                    news_time_str = '00:00'
                news_dt = datetime.datetime.strptime(f'{search_dt_str} {news_time_str}', '%Y%m%d %H:%M')
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'mosday job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru', config=config.newspaper_config)
                article.download()
                article.parse()
                data = {
                    'source': 'mosday',
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
    mosday_parser()
