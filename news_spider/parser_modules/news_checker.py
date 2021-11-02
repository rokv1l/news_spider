import random
from time import sleep
from datetime import datetime, date, timedelta

from loguru import logger

from config import request_delay
from src.database import news_db_col, changed_news_col
from parser_modules.parsers import page_parser


def news_checker():
    """Посещает страницы новостей и проверяет на изменения или удаление"""
    start = datetime.fromisoformat(f'{date.today().isoformat()}T00:00:00')
    end = start + timedelta(days=1)
    while True:
        news = list(news_db_col.find({'datetime': {'$gte': start, '$lt': end}}, {'_id': 0}))
        random.shuffle(news)
        for news_item in news:
            data = page_parser(news_item['url'])
            if not data:
                # Декоратор функции parse_news сам сделает лог об ошибке
                continue
            elif data == 404:
                logger.info(f'find deleted from site article {news_item["url"]}')
                changed_news_col.insert_one({
                    'url': news_item['url'],
                    'title': news_item['title'],
                    'content': news_item['content'],
                    'datetime': datetime.now().isoformat(),
                    'action': 'deleted'
                })
            else:
                logger.info(f'find changed article {news_item["url"]}')
                title, text, publish_date = data
                if title != news_item['title'] or text != news_item['content']:
                    changed_news_col.insert_one({
                        'url': news_item['url'],
                        'title': title,
                        'content': text,
                        'datetime': datetime.now().isoformat(),
                        'action': 'changed'
                    })
            sleep(request_delay)
        start -= timedelta(days=1)
        end -= timedelta(days=1)
