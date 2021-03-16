. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# change lint.sh if this is changed!
python3.8 -m black --line-length 200 duckbot tests
