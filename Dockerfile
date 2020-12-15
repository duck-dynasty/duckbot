FROM python:3.8
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
COPY duckbot/ /duckbot
COPY .env /duckbot/.env
WORKDIR /duckbot
CMD [ "python", "./main.py" ]