from discord.ext import commands
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class Database(commands.Cog, name="db"):
    def __init__(self, bot):
        self.bot = bot
        self.db = create_engine("postgresql+psycopg2://duckbot:pond@postgres/duckbot", echo=True, pool_pre_ping=True)

    @commands.command(name="db")
    async def test_command(self, context):
        with self.db.connect() as conn:
            result = conn.execute(text("SELECT * FROM weather_locations"))
            for row in result:
                print(f"{row}")
                await context.send(f"{row}")

    def session(self, item_type):
        item_type.metadata.create_all(self.db)
        Session = sessionmaker(self.db)
        return Session()
