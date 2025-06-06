# collect pip dependencies into a virtualenv, which we'll copy into the prod stage
FROM python:3.10 as pip-dependencies
ENV VIRTUAL_ENV "/opt/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"
WORKDIR /pip-dependencies
# install atlas for numpy (matplotlib dependency)
RUN apt-get update && apt-get -y install \
    libatlas-base-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY scripts/ ./scripts
COPY pyproject.toml .
RUN pip install .
RUN setup_nltk

FROM python:3.10-slim as prod
# ffmpeg: for discord audio
# libpq-dev: postgres client libraries
# libatlas-base-dev: matplotlib dependencies
# fortune/cowsay: for !fortune command
RUN apt-get update && apt-get -y install \
    ffmpeg \
    libpq-dev \
    libatlas-base-dev \
    fortune-mod fortunes cowsay \
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
