FROM python:3.12-slim

WORKDIR /app

COPY . /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && \
    apt-get install -y tzdata && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get install -y xvfb zip wget curl psmisc supervisor gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-bin libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils libgbm-dev libcurl3-gnutls ffmpeg libffi-dev build-essential
RUN apt-get -y install dbus-x11 xfonts-base xfonts-100dpi xfonts-75dpi xfonts-cyrillic xfonts-scalable
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_123.0.6312.58-1_amd64.deb -O google-chrome-stable.deb \
    && dpkg -i google-chrome-stable.deb || apt-get install -fy \
    && rm google-chrome-stable.deb

# install dependenciesz
RUN apt-get update \
    && apt-get -y install libpq-dev gcc
RUN apt-get update && \
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

# Install pipenv
RUN pip install pipenv

# Install required system packages
RUN apt-get update && apt-get install -y python3-distutils

# Install dependencies defined in Pipfile.lock
RUN pipenv install --deploy --ignore-pipfile



# Copy environment variables and supervisor config
COPY .env /app/

