import logging
import logging.handlers
import os


def define_logs():
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)

    handler = logging.handlers.RotatingFileHandler(filename=os.path.join(log_directory, "duck.log"), mode="a", maxBytes=256000, backupCount=10)
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))

    discord = logging.getLogger("discord")
    discord.setLevel(logging.INFO)
    discord.addHandler(handler)

    duckbot = logging.getLogger("duckbot")
    duckbot.setLevel(logging.INFO)
    duckbot.addHandler(handler)
