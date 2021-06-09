FROM python:3
WORKDIR /api
COPY requirements.txt /api
RUN pip install --no-cache-dir -r requirements.txt
COPY /api /api
CMD ["python3", "app.py"]