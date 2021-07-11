import datetime
import logging
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article

import config


from src.database import news_db_col, errors_db_col


def moskva_tyt_parser():
    print(f'moskva_tyt job started at {datetime.datetime.now()}')
    search_dt = datetime.datetime.now().date()
    while True:
        r = requests.get(f'https://www.moskva-tyt.ru/news/{search_dt.isoformat().replace("-", "")}.html')
        if r.status_code != 200:
            print(
                f'moskva_tyt job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_list = soup.find_all('div', {'class': 'next'})
        for news in news_list:
            try:
                news_url = 'https://www.moskva-tyt.ru' + news.find('a').get('href')
                if news_db_col.find_one({'url': news_url}):
                    print(f'moskva_tyt job ended at {datetime.datetime.now()}')
                    return
                r = requests.get(news_url, allow_redirects=True)
                if r.status_code != 200:
                    print(
                        f'moskva_tyt job error, request status code != 200\n'
                        f'url: {r.url}\n'
                        f'status code: {r.status_code}\n'
                        f'at {datetime.datetime.now()}'
                    )
                    return
                soup = BeautifulSoup(r.text, 'lxml')
                news_time_str = soup.find('span', {'class': 'datenews'}).text
                months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября',
                          'Октября', 'Ноября', 'Декабря']
                m_num = months.index(news_time_str[3:-11])
                news_time_str = news_time_str[:3] + f'{m_num if m_num > 9 else f"0{m_num}"}' + news_time_str[-11:]
                news_dt = datetime.datetime.strptime(news_time_str, '%d %m %Y %H:%M')
                if news_dt < datetime.datetime.now() - datetime.timedelta(**config.tracked_time):
                    print(f'moskva_tyt job ended at {datetime.datetime.now()}')
                    return
                article = Article(news_url, language='ru', config=config.newspaper_config)
                article.set_html(r.text)
                article.parse()
                data = {
                    'source': 'moskva_tyt',
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
    moskva_tyt_parser()
