FROM python:3.12-slim

WORKDIR /app

COPY . /app

# Install pipenv
RUN pip install pipenv

# Install dependencies defined in Pipfile.lock
RUN pipenv install --deploy --ignore-pipfile

# Install supervisor using pipenv
RUN pipenv install supervisor

# Copy environment variables and supervisor config
COPY .env /app/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Use pipenv to run supervisor
CMD ["pipenv", "run", "supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
