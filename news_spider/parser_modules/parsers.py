
import re
import newspaper
from datetime import datetime
from loguru import logger

from newspaper import Config, ArticleException

from src.database import news_db_col

newspaper_config = Config()
newspaper_config.request_timeout = 3


@logger.catch()
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


@logger.catch()
def portal_parser(url):
    news_paper = newspaper.build(url, language='ru', memoize_articles=False)

    # Возможно этот блок кода не нужен
    pattern_1 = r'https?:\/\/.+\.\w+($|\/)'
    pattern_2 = r'\w+\.\w+($|\/)'
    domen = re.search(pattern_1, url)
    if not domen:
        logger.warning(f'Something went wrong, domen is None. Url is {url}')
        return
    domen = re.search(pattern_2, domen.group()).group()[:-1]
    # --------------------------------

    for article in news_paper.articles:
        if domen not in article.url:
            continue
        if news_db_col.find_one({'url': article.url}):
            continue
        data = page_parser(article.url)
        if data == 404 or not data:
            continue
        news_db_col.insert_one({
            'source': url,
            'url': article.url,
            'title': data[0],
            'content': data[1],
            'datetime': datetime.now().isoformat()
        })
