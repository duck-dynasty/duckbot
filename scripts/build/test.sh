. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# test with pytest and gather code coverage
python -m coverage run --source=duckbot/ -m pytest -ra && \

# when tests pass, output coverage report
python -m coverage report --show-missing --skip-empty --skip-covered --fail-under=80 && \

# generate html coverage report
python -m coverage html && echo "html report: file://$(pwd)/htmlcov/index.html"
