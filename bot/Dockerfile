FROM python:3
WORKDIR /bot
COPY requirements.txt /bot
RUN pip install --no-cache-dir -r requirements.txt
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY /bot /bot
CMD ["python3", "app.py"]