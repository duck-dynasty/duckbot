from discord.ext import commands
import psycopg2
from sqlalchemy import create_engine, text


class Database(commands.Cog, name="db"):
    def __init__(self, bot):
        self.bot = bot
        self.db = create_engine("postgresql+psycopg2://postgres:postgres@postgres/postgres", echo=True)

    @commands.command(name="db")
    async def test_command(self, context):
        with self.db.connect() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS some_table (x int, y int)"))
            # conn.execute(text("INSERT INTO some_table (x, y) VALUES (:x, :y)"), [{"x": 1, "y": 1}, {"x": 2, "y": 4}])
            result = conn.execute(text("SELECT x, y FROM some_table"))
            for row in result:
                print(f"x: {row.x}  y: {row.y}")
