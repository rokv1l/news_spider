from time import sleep
from datetime import datetime
from traceback import format_exc

import newspaper
from newspaper import ArticleException, Article
from pymongo import MongoClient

import config
from config import newspaper_config, get_logger, logs_path, mongo_ip, mongo_port

logger = get_logger(__name__, logs_path + __name__ + '.log', backups=2)


def page_parser(url):
    logger.debug(f'page_parser {url}')
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
    logger.debug(f'portal_parser {url}')
    try:
        # memoize_articles True говорит о том что уже полученные новости будут сохраняться в кеш и больше не будут получаться
        news_paper = newspaper.build(url, language='ru', memoize_articles=True, config=newspaper_config)
        # это странное решение принято для оптимизации т.к. news_paper кушает слишком много памяти
        articles = [article.url for article in news_paper.articles]
        del news_paper
        count = 0
        for article_url in articles:
            with MongoClient(mongo_ip, mongo_port) as client:
                if client.news_parser.news.find_one({'url': article_url}):
                    continue
                data = page_parser(article_url)
                if data == 404 or not data or not data[1] or not data[0]:
                    continue
                if not data[2] or data[2].replace(tzinfo=None) > datetime.now().replace(tzinfo=None):
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
                client.close()
        logger.info(f'found {count} new news in {url} at {datetime.now()}')
    except Exception:
        logger.exception(format_exc())
        raise
