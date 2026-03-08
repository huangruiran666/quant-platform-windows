
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install akshare flask gunicorn
CMD exec gunicorn --bind :$PORT --workers 4 --threads 8 --timeout 0 main:app

