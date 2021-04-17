#!/bin/bash

_term() {
    echo "in term"
    kill "$bot"
}

trap _term SIGTERM

python -u -m duckbot "$DUCKBOT_ARGS" &

bot=$!

wait "$bot"
