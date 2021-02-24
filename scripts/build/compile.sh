. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# try to execute duckbot, but skip starting the bot
python3.8 duckbot/main.py dry-run
