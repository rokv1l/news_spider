from os import getenv

from newspaper import Config

mongo_ip = getenv('MONGO_IP')
mongo_port = int(getenv('MONGO_PORT'))

run_jobs_delay = 60*60
request_delay = 5
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
