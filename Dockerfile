# runs duckbot; requires duckbot/.env to be available which contains api tokens
FROM python:3.8
RUN apt-get update && apt-get -y install \
    ffmpeg \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --upgrade pip
COPY requirements.txt /
RUN python -m pip install -r /requirements.txt
COPY resources/ /duckbot/resources
COPY duckbot/ /duckbot/duckbot
WORKDIR /duckbot
HEALTHCHECK --retries=5 --start-period=60s --interval=60s \
  CMD python -m duckbot.health || exit 1
ENV DUCKBOT_ARGS ""
CMD [ "sh", "-c", "python -u -m duckbot $DUCKBOT_ARGS" ]
