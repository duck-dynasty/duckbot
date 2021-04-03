# run black formatter on the code
python -m black "$(git rev-parse --show-toplevel)/duckbot" "$(git rev-parse --show-toplevel)/tests"
