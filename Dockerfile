FROM python:3.8 as compile
RUN mkdir /wheels
WORKDIR /compile
COPY setup.py .
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip wheel . --wheel-dir=/wheels

FROM python:3.8
RUN apt-get update && apt-get -y install \
    ffmpeg \
    fortune-mod fortunes fortunes-off cowsay cowsay-off \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH "$PATH:/usr/games"
WORKDIR /duckbot
COPY --from=compile /root/nltk_data /root/nltk_data
COPY --from=compile /wheels /tmp/wheels
COPY setup.py .
COPY resources/ ./resources
COPY duckbot/ ./duckbot
RUN python -m pip install --no-index --find-links=/tmp/wheels/. .
ENV DUCKBOT_ARGS ""
ENTRYPOINT [ "python" ]
CMD [ "-u", "-m", "duckbot" ]
