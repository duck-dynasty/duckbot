# runs duckbot; requires duckbot/.env to be available which contains api tokens
FROM python:3.8
COPY healthcheck/ /duckbot/healthcheck
COPY requirements.txt /
RUN python -m pip install --upgrade pip
RUN python -m pip install -r /requirements.txt
COPY duckbot/ /duckbot/duckbot
WORKDIR /duckbot
HEALTHCHECK --retries=5 --start-period=60s --interval=60s \
  CMD python -m healthcheck || exit 1
CMD [ "python", "-u", "-m", "duckbot" ]
