FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install pipenv

RUN pipenv install --deploy --ignore-pipfile

RUN pip install supervisor

COPY .env /app/

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
