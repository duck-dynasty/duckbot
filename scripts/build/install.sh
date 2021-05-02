# install apt dependencies; ffmpeg and postgres are needed to run unit tests
# sudo apt-get install -y --no-install-recommends \
#     ffmpeg \
#     libpq-dev \
#     && \

# upgrade venv pip
python -m pip install --upgrade pip && \

# install package requirements
python -m pip install -r "$(git rev-parse --show-toplevel)/requirements.txt" && \

# install test and build dependencies
python -m pip install -r "$(git rev-parse --show-toplevel)/requirements-dev.txt"
