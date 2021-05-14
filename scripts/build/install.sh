# install apt dependencies; ffmpeg and postgres are needed to run unit tests
if [[ "$1" != "actions" ]]; then
    sudo apt-get install -y --no-install-recommends \
        ffmpeg \
        libpq-dev
fi && \

# upgrade venv pip
python -m pip install --upgrade pip && \

# install package requirements
python -m pip install --upgrade -r "$(git rev-parse --show-toplevel)/requirements.txt" && \

# install test and build dependencies
python -m pip install -r "$(git rev-parse --show-toplevel)/requirements-dev.txt" && \

# install nltk packages for tests (mocking this stuff is impossible)
for package in "cmudict"; do
    python -c "import os; import nltk; nltk.download('$package', download_dir=None if os.getenv('VIRTUAL_ENV') is None else os.path.join('$VIRTUAL_ENV', 'nltk_data'))"
done
