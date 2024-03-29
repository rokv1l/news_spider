from loguru import logger
import os
from logging.handlers import RotatingFileHandler
from os import getenv

from newspaper import Config

logs_path = getenv('LOGS_PATH')

if not os.path.exists(logs_path):
    os.makedirs(logs_path)

logger.add(f'{logs_path}data.log', format="{name} {time} {level} {message}", level="DEBUG", rotation='5MB', compression='zip')

urls = (
        'https://aif.ru',
        'https://bezformata.com/',
        'https://www.bfm.ru',
        'https://echo.msk.ru/',
        'https://icmos.ru/',
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
        'https://www.moskva-tyt.ru',    # тут возможно забанили при тестах
        'https://moslenta.ru',
        'https://mtdi.mosreg.ru/',
        'https://mperspektiva.ru/',
        'http://msk-news.net/',
        'https://msknovosti.ru/',
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

max_pull_lenth = 3
main_loop_delay = 30
