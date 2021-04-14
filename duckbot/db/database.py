from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database(commands.Cog, name="db"):
    def __init__(self, bot):
        self.bot = bot
        self.db = create_engine("postgresql+psycopg2://duckbot:pond@postgres/duckbot", pool_pre_ping=True)

    def session(self, item_type):
        item_type.metadata.create_all(self.db)
        Session = sessionmaker(self.db)
        return Session()
