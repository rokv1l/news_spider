from loguru import logger
from time import sleep
from threading import Thread

import config
from parser_modules.parsers import portal_parser
from parser_modules.news_checker import news_checker


def demon(urls):
    while True:
        for url in urls:
            try:
                portal_parser(url)
            except Exception:
                logger.exception('Something went wrong')

def main():
    Thread(target=portal_parser, args=(config.urls, ), daemon=True).start()
    Thread(target=news_checker, daemon=True).start()


if __name__ == '__main__':
    main()
