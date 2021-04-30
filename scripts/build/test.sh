. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# test with pytest and gather code coverage
python -m pytest \
    -ra \
    --black \
    --flake8 \
    --cov=$(d="${1/tests/duckbot}" ; echo "${d:-duckbot}") \
    --cov-branch \
    --cov-fail-under=85 \
    --cov-report html \
    --cov-report term-missing:skip-covered \
    -n auto \
    --blockage \
    "$1"

echo "html report: file://$(pwd)/htmlcov/index.html"
