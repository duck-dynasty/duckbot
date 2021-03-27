. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# stop the build if there are python syntax errors or undefined names
python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics && \

# exit-zero treats all errors as warnings
python -m flake8 . --count --exit-zero --statistics && \

# check if the format is correct
python -m black --diff --check duckbot tests
