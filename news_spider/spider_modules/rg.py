import datetime
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def rg_parser():
    print(f'rg job started at {datetime.datetime.now()}')
    limit = 25
    offset = 0
    while True:
        url = f'https://rg.ru/region/cfo/stolica/kind-article/json/b-news-inner/{limit}/{offset}.json'
        r = requests.get(url)
        if r.status_code != 200:
            print(
                f'rg job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        data = r.json()
        if not data.get('result'):
            return
        for article in data.get('result'):
            try:
                soup = BeautifulSoup(article, 'lxml')
                news_url = f'https://rg.ru' + soup.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'rg job ended at {datetime.datetime.now()}')
                    return
                r = requests.get(news_url)
                soup = BeautifulSoup(r.text, 'lxml')
                news_dt_tag = soup.find('div', {'class': 'b-material-head__date'})
                str_date = news_dt_tag.find('span', {'class': 'b-material-head__date-day'}).text
                str_time = news_dt_tag.find('span', {'class': 'b-material-head__date-time'}).text
                news_dt = datetime.datetime.fromisoformat(f'{str_date[-4:]}-{str_date[3:5]}-{str_date[:2]}T{str_time}:00')
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'rg job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.set_html(r.text)
                article.parse()
                data = {
                    'source': 'rg',
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
    rg_parser()
