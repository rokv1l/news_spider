from loguru import logger
from time import sleep
from threading import Thread

import config
from parser_modules.parsers import portal_parser
from parser_modules.news_checker import news_checker


def demon():
    while True:
        for url in config.urls:
            try:
                portal_parser(url)
                logger.info(f'{url} parsed successful')
            except Exception:
                logger.exception('Something went wrong')

def main():
    t = Thread(target=demon)
    t.start()
    Thread(target=news_checker, daemon=True).start()
    t.join()

if __name__ == '__main__':
    main()
