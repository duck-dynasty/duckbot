# upgrade venv pip
python -m pip install --upgrade pip && \

# install package requirements
python -m pip install -r "$(git rev-parse --show-toplevel)/requirements.txt" && \

# install test and build dependencies
python -m pip install -r "$(git rev-parse --show-toplevel)/requirements-dev.txt"
