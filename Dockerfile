FROM python:3.8-slim
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
COPY src/ /app
WORKDIR /app
CMD [ "python", "./duckbot/main.py" ]