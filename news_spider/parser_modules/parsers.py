
import newspaper
from time import sleep
from datetime import datetime
from loguru import logger

from newspaper import ArticleException, Article

import config
from config import newspaper_config

from pymongo import MongoClient

from config import mongo_ip, mongo_port


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
    news_paper = newspaper.build(url, language='ru')
    with MongoClient(mongo_ip, mongo_port) as client:
        count = 0
        for article in news_paper.articles:
            if client.news_parser.news.find_one({'url': article.url}):
                continue
            data = page_parser(article.url)
            if data == 404 or not data or not data[1] or not data[0]:
                continue
            client.news_parser.news.insert_one({
                'source': url,
                'url': article.url,
                'title': data[0],
                'content': data[1],
                'datetime': datetime.now().isoformat()
            })
            count += 1
            sleep(config.request_delay)
    del news_paper
    logger.info(f'found {count} new news in {url} at {datetime.now()}')
