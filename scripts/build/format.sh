. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# run black formatter on the code
python -m black duckbot tests
