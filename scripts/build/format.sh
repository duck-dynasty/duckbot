. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# run black formatter on the code
python3.8 -m black duckbot tests
