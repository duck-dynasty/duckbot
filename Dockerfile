# runs duckbot; requires duckbot/.env to be available which contains api tokens
FROM python:3.8
RUN apt-get update && apt-get -y install \
    ffmpeg \
    sqlite3 libsqlite3-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /
RUN python -m pip install --upgrade pip
RUN python -m pip install -r /requirements.txt
COPY duckbot/ /duckbot/duckbot
WORKDIR /duckbot
CMD [ "python", "-u", "-m", "duckbot" ]
