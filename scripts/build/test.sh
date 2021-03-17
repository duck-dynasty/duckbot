. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# test with pytest and gather code coverage
python3.8 -m coverage run --source=duckbot/ -m pytest -s && \

# when tests pass, output coverage report
python3.8 -m coverage report --show-missing --skip-empty --skip-covered --fail-under=80
