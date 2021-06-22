# https://www.msk.kp.ru/online/
import json
import datetime
import traceback
from time import sleep

import requests
from newspaper import Article

import config
from src.database import news_db_col, errors_db_col


def kp_parser():
    print(f'kp job started at {datetime.datetime.now()}')
    page = 1000
    while True:
        if page == 0:
            print(f'kp job ended at {datetime.datetime.now()}')
            return
        r = requests.get(
            'https://s8.stc.m.kpcdn.net/content/api/1/pages/get.json/result/',
            params={
                'pages.number': page,
                'pages.direction': 'page',
                'pages.target.id': 1,
                'pages.target.class': 100,
            })
        if r.status_code != 200:
            print(
                f'kp job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        raw_data = r.json()
        news_list = raw_data.get('childs')
        for news in news_list:
            try:
                news_url = 'https://www.msk.kp.ru/online/news/' + str(news['@id'])
                if news_db_col.find_one({'url': news_url}):
                    print(f'kp job ended at {datetime.datetime.now()}')
                    return
                news_dt = datetime.datetime.fromisoformat(news['meta'][0]['value'])
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'kp job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru')
                article.download()
                article.parse()
                data = {
                    'source': 'kp',
                    'url': news_url,
                    'title': article.title,
                    'content': article.text,
                    'datetime': news['meta'][0]['value']
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
        page = int(raw_data['meta'][1]['value']) - 1


if __name__ == '__main__':
    kp_parser()


