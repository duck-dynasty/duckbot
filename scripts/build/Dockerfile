# attempt to build and test duckbot
# should this docker image build, dockbot *should* be able to run
FROM python:3.8 as python
COPY . /duckbot
WORKDIR /duckbot
RUN python -m pip install --upgrade pip
RUN [ "/bin/bash", "-c", ". scripts/build/install.sh" ]
RUN [ "/bin/bash", "-c", ". scripts/build/compile.sh" ]
RUN [ "/bin/bash", "-c", ". scripts/build/test.sh" ]
RUN [ "/bin/bash", "-c", ". scripts/build/lint.sh" ]
