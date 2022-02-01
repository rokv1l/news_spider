import json
import requests
from datetime import datetime
from time import sleep

params = {
    'limit': 1000,
    'offset': 0
}
news = []
while True:
    try:
        r = requests.get(
            'http://45.141.78.97:5001/get_news',
            headers={'authorization': 'Bearer 08bbc13ad207e1a6949a07b63f38f2f35b2f7d9db47dfe6d614c2be74e701604'},
            params=params,
            timeout=25
        )
        if r.status_code != 200:
            print(f'status_code {r.status_code}! Try again in 10 secs')
            sleep(10)
            continue
        if not r.json():
            break
        news.extend(r.json())
        params['offset'] += params['limit']
        print(f'downloaded {len(news)} news')
    except Exception:
        print(f'Something went wrong, try again in 10 secs')
        sleep(10)
        continue

with open(f'news_{len(news)}_{datetime.now().strftime("%d_%m_%Y")}.json', 'w', encoding='utf-8') as f:
    json.dump(news, f, ensure_ascii=False)
