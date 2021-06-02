import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

from src.database import news_db_col


def riamo_parser():
    print(f'riamo job started at {datetime.datetime.now()}')
    params = {'type': 'all'}
    while True:
        r = requests.get(f'https://riamo.ru/ajax/news.xl', params=params)
        if r.status_code != 200:
            print(f'm24 job ended at {datetime.datetime.now()}')
            return
        if params == {'type': 'all'}:
            params['offset'] = 0
            params['main'] = 1
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find_all('div', {'class': 'card-horizontal'})
        for news in news_list:
            news_url = 'https://riamo.ru' + news.find('a').get('href')
            if news_db_col.find_one({'url': news_url}):
                print(f'riamo job ended at {datetime.datetime.now()}')
                return
            r = requests.get(news_url)
            if r.status_code != 200:
                print(f'm24 job ended at {datetime.datetime.now()}')
                return
            soup = BeautifulSoup(r.text, 'lxml')
            news_dt_str = soup.find('time', {'class': 'heading--time'}).find('meta', {'itemprop': 'datePublished'}).get('content')
            news_dt = datetime.datetime.fromisoformat(news_dt_str.replace('+03', '') + ':00')
            if news_dt < datetime.datetime.now() - datetime.timedelta(days=30):
                print(f'riamo job ended at {datetime.datetime.now()}')
                return
            article = Article(news_url, language='ru')
            try:
                article.set_html(r.text)
                article.parse()
            except Exception:
                print(1)
                continue
            data = {
                'source': 'riamo',
                'url': news_url,
                'title': article.title,
                'content': article.text,
                'datetime': news_dt
            }
            news_db_col.insert_one(data)
            params['last'] = int(news.get('data-flatr').replace('article', ''))
            sleep(1)
        params['offset'] += 10


if __name__ == '__main__':
    riamo_parser()
