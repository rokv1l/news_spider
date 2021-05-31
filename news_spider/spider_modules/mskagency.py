import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

from src.database import news_db_col


def mskagency_parser():
    print(f'mskagency job started at {datetime.datetime.now()}')
    page = 1
    while True:
        url = 'https://www.mskagency.ru'
        params = {'page': page, 'rnd': 1}
        r = requests.get(url, params=params)
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find('ul', {'class': 'NewsList'}).find_all('li')
        for news in news_list:
            if news.get('class') == ['date']:
                continue
            news_date_str = news.get('data-datei')
            news_time_str = news.find('div', {'class': 'time'}).text
            news_dt = datetime.datetime.fromisoformat(f'{news_date_str[:4]}-{news_date_str[4:6]}-{news_date_str[6:]}T{news_time_str}:00')
            if news_dt < datetime.datetime.now() - datetime.timedelta(days=30):
                print(f'mskagency job ended at {datetime.datetime.now()}')
                return
            news_url = url + news.find('a').get('href')
            if news_db_col.find_one({'url': news_url}):
                print(f'mskagency job ended at {datetime.datetime.now()}')
                return
            else:
                article = Article(news_url, language='ru')
                try:
                    article.download()
                    article.parse()
                except Exception:
                    continue
                data = {
                    'source': 'mskagency',
                    'url': news_url,
                    'title': article.title,
                    'content': article.text,
                    'datetime': news_dt
                }
                news_db_col.insert_one(data)
        page += 1
        sleep(1)


if __name__ == '__main__':
    mskagency_parser()
