from os import getenv


mongo_ip = getenv('MONGO_IP')
mongo_port = int(getenv('MONGO_PORT'))

token = getenv('API_TOKEN')
