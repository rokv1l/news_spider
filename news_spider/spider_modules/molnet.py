import datetime
import traceback
import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from newspaper import Article
from newspaper import ArticleException

import config

from src.database import news_db_col, errors_db_col


def molnet_parser():
    print(f'molnet job started at {datetime.datetime.now()}')
    page = 1
    while True:
        params = {
            'page': page,
        }
        url = 'https://www.molnet.ru/mos/ru/news'
        r = requests.post(url, params=params)
        if r.status_code != 200:
            print(
                f'molnet job error, request status code != 200\n'
                f'url: {r.url}\n'
                f'status code: {r.status_code}\n'
                f'at {datetime.datetime.now()}'
            )
            return
        soup = BeautifulSoup(r.text, 'lxml')
        news_div = soup.find('div', {'class': 'l-col__inner'})
        news_list = news_div.find_all('a')

        for wer in news_list:
            if wer.has_attr('class'):
                if wer['class'][0] == 'itemlist__b-img':
                    news_list.remove(wer)
                elif wer['class'][0] == 'itemlist__author':
                    news_list.remove(wer)

        for i in news_list:
            if i.get('href').startswith('infocity') or i.get('href').startswith('vao'):
                news_list.remove(i)

        for news in news_list:
            try:
                news_url = news.get('href')
                news_db_url = f"http://www.molnet.ru{news_url}"
                if news_db_col.find_one({'url': news_db_url}):
                    print(f'molnet job ended at {datetime.datetime.now()}')
                    return

                if news_url.startswith('http'):
                    continue
                else:
                    if news.has_attr('class'):
                        if news['class'][0] == 'link-wr':
                            str_time = news.find('span', {'class': 'prelist-date'}).text.split("•")[-1]
                            str_time = str_time[1:]
                        elif news['class'][0] == 'itemlist__link':
                            if news.find_parent('div').find('p') is not None:
                                str_time = news.find_parent('div').find('p').find('span').text.split("•")[0]
                                str_time = str_time[:-1]
                            elif news.find_parent('div').find('p') is None:
                                if news_url.startswith('infocity') or news_url.startswith('vao'):
                                    page += 1
                                    break
                                else:
                                    str_time = news.find_parent('li').find('span').text.split("•")[-1]
                                    str_time = str_time[1:]
                    else:
                        continue

                dt_now = datetime.datetime.now()

                time_data = {
                    'hour': 0,
                    'minute': 0,
                    'second': 0,
                    'microsecond': 0,
                }

                if str_time == 'Вчера':
                    time_data.update({'year': dt_now.year, 'month': dt_now.month, 'day': dt_now.day - 1})
                elif re.findall(r'^\d{2}:\d{2}$', str_time):
                    time_data.update(
                        {'year': dt_now.year, 'month': dt_now.month, 'day': dt_now.day, 'hour': int(str_time[:2]),
                         'minute': int(str_time[-2:])})
                elif re.findall(r'^\d{2}\.\d{2}\.\d{4}$', str_time):
                    time_data.update(
                        {'year': int(str_time[6:10]), 'month': int(str_time[3:5]), 'day': int(str_time[:2])})

                news_dt = datetime.datetime(**time_data)
                if news_dt < dt_now - datetime.timedelta(**config.tracked_time):
                    print(f'molnet job ended at {datetime.datetime.now()}')
                    return
                try:
                    article = Article(news_db_url, language='ru', config=config.newspaper_config)
                    article.download()
                    article.parse()
                except Exception:
                    continue
                data = {
                    'source': 'molnet',
                    'url': news_db_url,
                    'title': article.title,
                    'content': article.text,
                    'datetime': news_dt.isoformat()
                }
                print(news_url)
                news_db_col.insert_one(data)
            except Exception as e:
                print(e)
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
    molnet_parser()
