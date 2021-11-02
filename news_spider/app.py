from time import sleep
from multiprocessing import Process, freeze_support

import config
from parser_modules.parsers import portal_parser
from parser_modules.news_checker import news_checker
from src.sсhedule_mp import IntervalJob, Scheduler

freeze_support()


def main():
    urls = (
        'https://aif.ru',
        # 'https://as6400825.ru',  # Сайт сломан, требует от меня установелнный php, бред
        'https://bezformata.com/',
        'https://www.bfm.ru',
        'https://echo.msk.ru/',
        'https://icmos.ru/',
        # 'https://msk.inregiontoday.ru',  # Паук не может распарсить этот сайт
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
        # 'http://mosday.ru/news',    # Паук не может распарсить этот сайт
        'https://www.moskva-tyt.ru',    # тут возможно забанили при тестах
        'https://moslenta.ru',
        'https://mtdi.mosreg.ru/',
        'https://mperspektiva.ru/',
        'http://msk-news.net/',
        # 'https://www.mskagency.ru',  # Паук не может распарсить этот сайт
        'https://msknovosti.ru/',
        # 'https://novayagazeta.ru/',  # Паук не может распарсить этот сайт
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
    count = 0
    Process(target=news_checker).start()
    for paper in urls:
        if count >= 10:
            count = 0
            sleep(60*5)
        process = Process(target=portal_parser, args=(paper, ))
        process.daemon = True
        process.start()
        scheduler.add_job(IntervalJob(paper, portal_parser, args=(paper, ), delay=config.run_jobs_delay))
        count += 1
    scheduler.run_pending()


if __name__ == '__main__':
    main()
