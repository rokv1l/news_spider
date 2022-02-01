
from time import sleep
from datetime import datetime

import newspaper
from newspaper import ArticleException, Article
from loguru import logger
from pymongo import MongoClient
from pymongo.errors import AutoReconnect, ServerSelectionTimeoutError

import config
from config import newspaper_config, logs_path, mongo_ip, mongo_port


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
    news_paper = newspaper.build(url, language='ru', memoize_articles=True, config=newspaper_config)
    while True:
        try:
            count = 0
            with MongoClient(mongo_ip, mongo_port) as client:
                for article in news_paper.articles:
                    while True:
                        try:
                            if client.news_parser.news.find_one({'url': article.url}):
                                continue
                            data = page_parser(article.url)
                            if data == 404 or not data or not data[1] or not data[0]:
                                continue
                            if not data[2] or data[2].replace(tzinfo=None) > datetime.now().replace(tzinfo=None):
                                data[2] = datetime.now().isoformat()
                            client.news_parser.news.insert_one({
                                'source': url,
                                'url': article.url,
                                'title': data[0],
                                'content': data[1],
                                'datetime': data[2]
                            })
                            break
                        except (AutoReconnect, ServerSelectionTimeoutError):
                            pass
                    count += 1
                    sleep(config.request_delay)
            sleep(config.run_jobs_delay)
        except Exception:
            logger.exception('Error')

