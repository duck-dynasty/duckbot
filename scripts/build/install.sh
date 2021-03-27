python -m pip install --upgrade pip && \

python -m pip install -r "$(git rev-parse --show-toplevel)/requirements.txt" && \

python -m pip install -r "$(git rev-parse --show-toplevel)/requirements-dev.txt"
