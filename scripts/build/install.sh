. "$(git rev-parse --show-toplevel)/env/prod/bin/activate" && \
python3.8 -m pip install -r "$(git rev-parse --show-toplevel)/requirements.txt" && \
deactivate && \

# activate test env
. "$(git rev-parse --show-toplevel)/env/dev/bin/activate" && \
python3.8 -m pip install -r "$(git rev-parse --show-toplevel)/requirements.txt" && \
python3.8 -m pip install -r "$(git rev-parse --show-toplevel)/requirements-dev.txt" && \
deactivate
