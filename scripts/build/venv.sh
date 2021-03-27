if [[ -z "$1" || "$1" = "build" ]]; then
    rm -rf "$(git rev-parse --show-toplevel)/env/" && \
    rm -rf "$(git rev-parse --show-toplevel)/ENV/" && \
    rm -rf "$(git rev-parse --show-toplevel)/venv/" && \
    rm -rf "$(git rev-parse --show-toplevel)/VENV/" && \
    python3.8 -m venv "$(git rev-parse --show-toplevel)/env/prod" && \
    python3.8 -m venv "$(git rev-parse --show-toplevel)/env/dev"
elif [[ "$1" = "deactivate" ]]; then
    deactivate
else
    . "$(git rev-parse --show-toplevel)/env/$1/bin/activate"
fi
# TODO just have `env`, have this script create/activate the env always, import from other scripts

# test if env is activated and activate; call this from every script
# which python && python --version == 3.8.x
# if it's the wrong version, delete + create + install
