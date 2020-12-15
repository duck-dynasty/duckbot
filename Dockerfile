FROM python:3.7
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
COPY duckbot/ /duckbot
WORKDIR /duckbot
CMD [ "python", "./main.py" ]