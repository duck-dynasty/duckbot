import logging
import logging.handlers
import os


def define_logging():
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)

    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(filename=os.path.join(log_directory, "duck.log"), mode="a", maxBytes=256000, backupCount=10)
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)
