. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# check for .env
if stat duckbot/.env > /dev/null 2>&1 && grep -q DISCORD_TOKEN duckbot/.env; then
    export $(cat duckbot/.env | xargs)
    # run duckbot, brother, for a max of 1h
    timeout 1h python3.8 -u -m duckbot || echo "we killed your idle duckbot"
else
    echo "No .env file or DISCORD_TOKEN not set. Yell at Tom to get the token."
fi
