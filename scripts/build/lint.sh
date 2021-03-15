. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# stop the build if there are Python syntax errors or undefined names
python3.8 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics && \

# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
python3.8 -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=200 --statistics && \

# check if the formatter ran; change format.sh if this is changed!
python3.8 -m black --line-length 200 --diff --check duckbot tests
