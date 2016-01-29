FROM python:3

MAINTAINER @bence

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["gunicorn", "30x_it.app:app", "--bind", ":8080", "--worker-class", "aiohttp.worker.GunicornWebWorker"]

EXPOSE 8080
