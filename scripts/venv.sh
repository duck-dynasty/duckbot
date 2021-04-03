if [[ -d "$(git rev-parse --show-toplevel)/venv/" ]]; then
    # a venv already exists
    if [[ -z "$(which python)" ]]; then
        # it's not active, activate it
        . "$(git rev-parse --show-toplevel)/venv/bin/activate"
    fi
    # test venv version number >= 3.8.0
    python -c 'import sys; import platform; from distutils.version import StrictVersion; sys.exit(0 if StrictVersion("3.8.0") <= StrictVersion(platform.python_version()) else 1)' 2>&1 /dev/null
    if [[ ! $? -eq 0 ]]; then
        # version is too low, create a new one
        which deactivate && deactivate
        rm -rf "$(git rev-parse --show-toplevel)/venv/" "$(git rev-parse --show-toplevel)/env/" "$(git rev-parse --show-toplevel)/ENV/" "$(git rev-parse --show-toplevel)/VENV/"
        python3.8 -m venv --clear --prompt duckbot "$(git rev-parse --show-toplevel)/venv/"
        . "$(git rev-parse --show-toplevel)/venv/bin/activate"
    fi
else
    # no venv, create one and activate it
    python3.8 -m venv --clear --prompt duckbot "$(git rev-parse --show-toplevel)/venv/"
    . "$(git rev-parse --show-toplevel)/venv/bin/activate"
fi
