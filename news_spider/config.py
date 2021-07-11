from os import getenv

from newspaper import Config

mongo_ip = getenv('MONGO_IP')
mongo_port = int(getenv('MONGO_PORT'))

run_jobs_delay = 60*60
request_delay = 7
tracked_time = {'days': 90}

newspaper_config = Config()
newspaper_config.request_timeout = 21
