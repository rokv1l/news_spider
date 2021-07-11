
import datetime
import traceback
from time import sleep

import requests
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def novayagazeta_parser():
    print(f'novayagazeta job started at {datetime.datetime.now()}')
    page = 0
    while True:
        r = requests.get(
            'https://novayagazeta.ru/api/v1/get/main',
            params={
                'c': 'novosti',
                'page': page,
            })
        if r.status_code != 200:
            print(
                f'novayagazeta job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        data = r.json()
        news_list = data.get('records')
        if not news_list:
            print(f'novayagazeta job ended at {datetime.datetime.now()}')
            return
        for news in news_list:
            try:
                news_url = 'https://novayagazeta.ru/articles/' + news['slug']
                if news_db_col.find_one({'url': news_url}):
                    print(f'novayagazeta job ended at {datetime.datetime.now()}')
                    return
                news_dt = datetime.datetime.fromtimestamp(int(str(news['date'])[:-3]))
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'novayagazeta job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru', config=config.newspaper_config)
                article.download()
                article.parse()
                data = {
                    'source': 'novayagazeta',
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
        page += 1


if __name__ == '__main__':
    novayagazeta_parser()
