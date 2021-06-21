from os import getenv

messaging_list = []

mongo_ip = getenv('MONGO_IP')
mongo_port = int(getenv('MONGO_PORT'))

telegram_token = getenv('TELEGRAM_TOKEN')
