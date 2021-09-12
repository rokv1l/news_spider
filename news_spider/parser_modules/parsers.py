from datetime import datetime
from loguru import logger
import newspaper

import config
from src.database import news_db_col


@logger.catch()
def page_parser(url):
    article = newspaper.Article(url, language='ru', config=config.newspaper_config)
    article.download()
    if article.download_state == 1:
        return 404
    article.parse()
    return tuple((article.title, article.text))


@logger.catch()
def portal_parser(url, checked_categories):
    news_paper = newspaper.build(url, language='ru')
    for article in news_paper.articles:
        if news_db_col.find_one({'url': article.url}):
            continue
        # TODO проверка домена ссылки на соответствие домену сайта
        data = page_parser(article.url)
        data = {
            'source': url,
            'url': article.url,
            'title': data[0],
            'content': data[1],
            'datetime': datetime.now().isoformat()
        }
    for category in news_paper.categories:
        if category.url in checked_categories:
            continue
        # TODO проверка домена ссылки на соответствие домену сайта
        checked_categories.append(category.url)
        portal_parser(category.url, checked_categories)



