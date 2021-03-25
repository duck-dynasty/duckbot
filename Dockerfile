# runs duckbot; requires .env to be available which contains api tokens
FROM python:3.8
COPY requirements.txt /
RUN python -m pip install --upgrade pip
RUN python -m pip install -r /requirements.txt
COPY duckbot/ /duckbot/duckbot
COPY .env /duckbot/.env
WORKDIR /duckbot
CMD [ "python", "-u", "-m", "duckbot" ]
