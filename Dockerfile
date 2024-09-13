FROM python:3.12-slim

WORKDIR /app

COPY . /app

# Install pipenv
RUN pip install pipenv

# Install required system packages
RUN apt-get update && apt-get install -y python3-distutils

# Install dependencies defined in Pipfile.lock
RUN pipenv install --deploy --ignore-pipfile


# Copy environment variables and supervisor config
COPY .env /app/

