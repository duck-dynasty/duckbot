# runs duckbot; requires duckbot/.env to be available which contains api tokens
FROM python:3.8
RUN apt-get update && apt-get -y install \
    ffmpeg \
    fortune-mod fortunes fortunes-off cowsay cowsay-off \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH "$PATH:/usr/games"
RUN python -m pip install --upgrade pip
WORKDIR /duckbot
COPY requirements.txt .
RUN python -m pip install -r ./requirements.txt
COPY resources/ ./resources
COPY duckbot/ ./duckbot
ENV DUCKBOT_ARGS ""
CMD [ "sh", "-c", "python -u -m duckbot $DUCKBOT_ARGS" ]
