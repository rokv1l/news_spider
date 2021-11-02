
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
        article = Article(url, language='ru', config=newspaper_config)
        article.download()
        if article.download_state == 1:
            return 404
        article.parse()
        return [article.title, article.text, article.publish_date]
    except ArticleException:
        return None


def portal_parser(url):
    # memoize_articles True говорит о том что уже полученные новости будут сохраняться в кеш и больше не будут получаться
    news_paper = newspaper.build(url, language='ru', memoize_articles=True, config=newspaper_config)
    # это странное решение принято для оптимизации т.к. news_paper кушает слишком много памяти
    articles = [article.url for article in news_paper.articles]
    del news_paper
    with MongoClient(mongo_ip, mongo_port) as client:
        count = 0
        for article_url in articles:
            if client.news_parser.news.find_one({'url': article_url}):
                continue
            data = page_parser(article_url)
            if data == 404 or not data or not data[1] or not data[0]:
                continue
            if not data[2] or datetime.fromisoformat(data[2]) > datetime.now():
                data[2] = datetime.now().isoformat()
            client.news_parser.news.insert_one({
                'source': url,
                'url': article_url,
                'title': data[0],
                'content': data[1],
                'datetime': data[2]
            })
            count += 1
            sleep(config.request_delay)
    logger.info(f'found {count} new news in {url} at {datetime.now()}')
