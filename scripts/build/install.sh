# install package requirements
if [[ -z "$1" || "$1" = "prod" ]]; then
    python3.8 -m pip install -r "$(git rev-parse --show-toplevel)/requirements.txt"
fi && \
# install test and build dependencies
if [[ -z "$1" || "$1" = "dev" ]]; then
    python3.8 -m pip install -r "$(git rev-parse --show-toplevel)/requirements-dev.txt"
fi
