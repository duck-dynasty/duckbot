# collect pip dependencies into a virtualenv, which we'll copy into the prod stage
FROM python:3.8 as pip-dependencies
ENV VIRTUAL_ENV "/opt/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"
WORKDIR /pip-dependencies
RUN pip install --upgrade pip setuptools wheel
COPY setup.py .
RUN pip install .

FROM python:3.8 as prod
RUN apt-get update && apt-get -y install \
    ffmpeg \
    libpq-dev \
    fortune-mod fortunes fortunes-off cowsay cowsay-off \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH "$PATH:/usr/games"
ENV VIRTUAL_ENV "/opt/venv"
ENV PATH "$VIRTUAL_ENV/bin:$PATH"
WORKDIR /duckbot
COPY --from=pip-dependencies "$VIRTUAL_ENV" "$VIRTUAL_ENV"
COPY resources/ ./resources
COPY duckbot/ ./duckbot
ENV DUCKBOT_ARGS ""
ENTRYPOINT [ "python" ]
CMD [ "-u", "-m", "duckbot" ]
