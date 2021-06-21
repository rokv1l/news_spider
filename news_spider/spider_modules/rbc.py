import datetime
import re
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def rbc_parser():
    print(f'rbc job started at {datetime.datetime.now()}')
    limit = 20
    offset = 0
    while True:
        url = 'https://www.rbc.ru/v10/ajax/get-news-by-story'
        params = {
            'story': '6009a4899a79471a2909f35a',
            'limit': limit,
            'offset': offset,
        }
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(
                f'rbc job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        html = r.json()['html']
        if not html:
            print(f'rbc job ended at {datetime.datetime.now()}')
            return
        soup = BeautifulSoup(html, 'lxml')
        news_list = soup.find_all('div', {'class': 'item'})
        for news in news_list:
            try:
                str_time = news.find('span', {'class': 'item__category'}).text
                dt_now = datetime.datetime.now()
                time_data = dict(
                    year=dt_now.year,
                    hour=int(str_time[-5:-3]),
                    minute=int(str_time[-2:]),
                    second=0,
                    microsecond=0
                )
                if re.findall(r'^\d\d:\d\d$', str_time):
                    time_data['month'] = dt_now.month
                    time_data['day'] = dt_now.day
                else:
                    month = ['янв', 'фев', 'мар', "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
                    time_data['month'] = int(month.index(str_time[3:6])+1)
                    time_data['day'] = int(str_time[:2])
                news_dt = datetime.datetime(**time_data)
                if news_dt < dt_now - datetime.timedelta(**config.tracked_time):
                    print(f'rbc job ended at {datetime.datetime.now()}')
                    return
                news_url = news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'rbc job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'rbc',
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
        offset += limit


if __name__ == '__main__':
    rbc_parser()
