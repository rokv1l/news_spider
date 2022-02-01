from time import sleep
from multiprocessing import Process, freeze_support

import config
from parser_modules.parsers import portal_parser
from parser_modules.news_checker import news_checker

freeze_support()


def main():
    count = 0
    for paper in config.urls:
        if count >= 5:
            count = 0
            sleep(60*5)
        process = Process(target=portal_parser, args=(paper, ))
        process.daemon = True
        process.start()
        count += 1
    Process(target=news_checker).start()


if __name__ == '__main__':
    main()
