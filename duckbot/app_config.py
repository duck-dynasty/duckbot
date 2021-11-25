import os


class AppConfig:
    """Utility class to house application configuration, such as running environment."""

    @staticmethod
    def _stage() -> str:
        return os.getenv("STAGE") or "test"

    @classmethod
    def is_production(cls) -> bool:
        """Returns True if DuckBot is running in a production environment.
        :return: True if this is prod"""
        return cls._stage() == "prod"
