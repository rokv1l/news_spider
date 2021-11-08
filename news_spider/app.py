from time import sleep
from multiprocessing import Process, freeze_support

import config
from parser_modules.parsers import portal_parser
from parser_modules.news_checker import news_checker
from src.sсhedule_mp import IntervalJob, Scheduler

freeze_support()


def main():
    scheduler = Scheduler()
    count = 0
    for paper in config.urls:
        if count >= 10:
            count = 0
            sleep(60*5)
        process = Process(target=portal_parser, args=(paper, ))
        process.daemon = True
        process.start()
        scheduler.add_job(IntervalJob(paper, portal_parser, args=(paper, ), delay=config.run_jobs_delay))
        count += 1
    Process(target=news_checker).start()
    scheduler.add_job(IntervalJob('news_checker', news_checker, delay=config.news_checker_delay))
    scheduler.run_pending()


if __name__ == '__main__':
    main()
