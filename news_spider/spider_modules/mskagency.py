import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup

from src.database import news_db_col


def mskagency_parser():
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
            print(news_dt)
            if news_dt < datetime.datetime.now() - datetime.timedelta(days=30):
                return
            news_url = url + news.find('a').get('href')
            print(news_url)
            if news_db_col.find_one({'url': news_url}):
                return
            else:
                news_db_col.insert_one({'url': news_url})
        page += 1
        sleep(1)


if __name__ == '__main__':
    mskagency_parser()
