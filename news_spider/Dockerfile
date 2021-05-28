FROM python:3
WORKDIR /news_spider
COPY requirements.txt /news_spider
RUN pip install --no-cache-dir -r requirements.txt
COPY /news_spider /news_spider
CMD ["python3", "app.py"]