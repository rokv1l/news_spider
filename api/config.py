import logging
import os
from logging.handlers import RotatingFileHandler
from os import getenv

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logs_path = getenv('LOGS_PATH')

if not os.path.exists(logs_path):
    os.mkdir(logs_path)


def get_logger(name, path, level=logging.INFO, size=1024*1024*5, backups=5):
    handler = RotatingFileHandler(path, maxBytes=size, backupCount=backups, encoding='utf-8')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


mongo_ip = getenv('MONGO_IP')
mongo_port = int(getenv('MONGO_PORT'))

token = getenv('API_TOKEN')
