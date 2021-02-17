. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# check for .env
if stat duckbot/.env > /dev/null 2>&1 && grep -q TOKEN duckbot/.env; then
    # run duckbot, brother
    python3.8 duckbot/main.py
else
    echo "No .env file or token not set. Yell at Tom to get the token."
fi
