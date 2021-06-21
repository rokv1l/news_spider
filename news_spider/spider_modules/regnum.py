
import datetime
import traceback
from time import sleep

import requests
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def regnum_parser():
    print(f'regnum job started at {datetime.datetime.now()}')
    page = 1
    while True:
        r = requests.get(
            'https://regnum.ru/api/get/search/news',
            params={
                'q': '',
                'page': page,
            })
        if r.status_code != 200:
            print(
                f'regnum job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        data = r.json()
        news_list = data.get('articles')
        for news in news_list:
            try:
                news_url = news['news_link']
                if news_db_col.find_one({'url': news_url}):
                    print(f'regnum job ended at {datetime.datetime.now()}')
                    return
                news_dt = datetime.datetime.fromtimestamp(news['news_date_unix'])
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'regnum job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'regnum',
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
        page += 1


if __name__ == '__main__':
    regnum_parser()
