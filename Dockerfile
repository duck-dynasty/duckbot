FROM python:3.8
RUN apt-get update && apt-get -y install \
    ffmpeg \
    libpq-dev \
    fortune-mod fortunes fortunes-off cowsay cowsay-off \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH "$PATH:/usr/games"
ENV VIRTUAL_ENV "/opt/venv"
ENV PATH "$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV
RUN pip install --upgrade pip setuptools wheel
WORKDIR /duckbot
COPY pyproject.toml .
COPY setup.py .
RUN pip install .
COPY resources/ ./resources
COPY duckbot/ ./duckbot
ENV DUCKBOT_ARGS ""
ENTRYPOINT [ "python" ]
CMD [ "-u", "-m", "duckbot" ]
