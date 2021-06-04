# collect pip dependencies into a virtualenv, which we'll copy into the prod stage
FROM python:3.8 as pip-dependencies
ENV VIRTUAL_ENV "/opt/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"
WORKDIR /pip-dependencies
RUN pip install --upgrade pip setuptools wheel
COPY pyproject.toml .
COPY setup.py .
RUN pip install --no-cache-dir --extra-index-url https://www.piwheels.org/simple .

FROM python:3.8-slim as prod
RUN apt-get update && apt-get -y install \
    ffmpeg \
    libpq-dev \
    libpulse-dev \
    libatlas-base-dev libgeos-dev \
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
