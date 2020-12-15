FROM python:3.7-slim
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
COPY src/ /app
WORKDIR /app
CMD [ "python", "./duckbot/main.py" ]