
from time import sleep
import newspaper
from datetime import datetime
from loguru import logger

from newspaper import ArticleException

import config
from src.database import news_db_col
from config import newspaper_config


def page_parser(url):
    try:
        article = newspaper.Article(url, language='ru', config=newspaper_config)
        article.download()
        if article.download_state == 1:
            return 404
        article.parse()
        return tuple((article.title, article.text))
    except ArticleException:
        return None


def portal_parser(url):
    news_paper = newspaper.build(url, language='ru', memoize_articles=False)

    tmp_count = 0
    for article in news_paper.articles:
        if news_db_col.find_one({'url': article.url}):
            continue
        data = page_parser(article.url)
        if data == 404 or not data or not data[1] or not data[0]:
            continue
        news_db_col.insert_one({
            'source': url,
            'url': article.url,
            'title': data[0],
            'content': data[1],
            'datetime': datetime.now().isoformat()
        })
        tmp_count += 1
        sleep(config.request_delay)
    logger.info(f'found {tmp_count} new news in {url} at {datetime.now()}')
