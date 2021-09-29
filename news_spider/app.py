from multiprocessing import Process, freeze_support

import config
from parser_modules.parsers import portal_parser
from src.sсhedule_mp import IntervalJob, Scheduler

freeze_support()


def main():
    papers = (
        'https://aif.ru',
        'https://as6400825.ru',
        'https://bezformata.com/',
        'https://www.bfm.ru',
        'https://echo.msk.ru/',
        'https://icmos.ru/',
        'https://msk.inregiontoday.ru',
        'https://www.interfax.ru/',
        'https://www.kommersant.ru/',
        'https://www.rostov.kp.ru/',
        'https://lenta.ru',
        'https://www.m24.ru/news',
        'https://mk.ru/news',
        'https://www.mn.ru/',
        'https://mockva.ru/',
        'https://www.molnet.ru',
        'https://moscow.ru.today/',
        'http://mosday.ru/news',
        'https://www.moskva-tyt.ru',
        'https://moslenta.ru',
        'https://mtdi.mosreg.ru/',
        'https://mperspektiva.ru/',
        'http://msk-news.net/',
        'https://www.mskagency.ru',
        'https://msknovosti.ru/',
        'https://novayagazeta.ru/',
        'https://www.pravda.ru/',
        'https://www.rbc.ru',
        'https://regnum.ru/',
        'https://rg.ru/',
        'https://ria.ru',
        'https://riamo.ru/',
        'https://russian.rt.com',
        'https://tass.ru',
        'https://tvrain.ru/',
        'https://vm.ru',
    )
    scheduler = Scheduler()
    for paper in papers:
        process = Process(target=portal_parser(paper))
        process.start()
        scheduler.add_job(IntervalJob(paper, portal_parser(paper), delay=config.run_jobs_delay))
    scheduler.run_pending()


if __name__ == '__main__':
    main()
