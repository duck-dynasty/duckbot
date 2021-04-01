. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

# try to execute duckbot, but skip starting the bot
python -m duckbot dry-run
