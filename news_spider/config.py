import logging
import os
from logging.handlers import RotatingFileHandler
from os import getenv

from newspaper import Config

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logs_path = '/opt/data/news_spider/'

if not os.path.exists(logs_path):
    os.mkdir(logs_path)


def get_logger(name, path, level=logging.INFO, size=1024*1024*5, backups=5):
    handler = RotatingFileHandler(path, maxBytes=size, backupCount=backups, encoding='utf-8')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


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

mongo_ip = getenv('MONGO_IP')
mongo_port = int(getenv('MONGO_PORT'))

run_jobs_delay = 60*60
request_delay = 5
news_checker_delay = 60*60*24*2
tracked_time = {'days': 90}

newspaper_config = Config()
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}
newspaper_config.headers = headers
newspaper_config.request_timeout = 10
newspaper_config.browser_user_agent = user_agent

