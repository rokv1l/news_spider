from loguru import logger
from time import sleep
from threading import Thread

import config
from parser_modules.parsers import portal_parser
from parser_modules.news_checker import news_checker


def main():
    Thread(target=news_checker, daemon=True).start()
    
    t_pull = []
    next_paper_index = 0
    while True:
        while len(t_pull) < config.max_pull_lenth:
            if next_paper_index >= len(config.urls):
                next_paper_index = 0
            t =  Thread(target=portal_parser, args=[config.urls[next_paper_index]])
            t.start()
            t_pull.append(t)
            next_paper_index += 1
        
        t_pull = [t for t in t_pull if t.is_alive()]
        sleep(config.main_loop_delay)



if __name__ == '__main__':
    main()
