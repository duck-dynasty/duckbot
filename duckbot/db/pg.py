import gzip
import io
import os
import subprocess
from typing import List, Optional

import discord
from discord.ext import commands

from duckbot.cogs.github.yolo_merge import is_repository_admin

from .database import Database

TIMEOUT = 120  # seconds


class Pg(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db

    @commands.group(name="pg", invoke_without_command=True)
    @commands.check(is_repository_admin)
    async def pg(self, context: commands.Context):
        await context.send("`!pg dump`, or `!pg restore` with the dump attached, brother.")

    @pg.command(name="dump")
    async def dump(self, context: commands.Context):
        async with context.typing():
            process = self.run(["pg_dump", "--clean", "--if-exists"])
            if process.returncode == 0:
                archive = discord.File(io.BytesIO(gzip.compress(process.stdout)), filename="duckbot.sql.gz")
                await context.author.send(file=archive)  # dumps hold everyone's saved locations, keep them out of the channel
                await context.send("Sent it to your DMs, brother.")
            else:
                await context.send(self.failure("pg_dump", process))

    @pg.command(name="restore")
    async def restore(self, context: commands.Context):
        async with context.typing():
            if context.message.attachments:
                attachment = context.message.attachments[0]
                dump = await attachment.read()
                if attachment.filename.endswith(".gz"):
                    dump = gzip.decompress(dump)
                process = self.run(["psql", "--variable", "ON_ERROR_STOP=1"], stdin=dump)
                if process.returncode == 0:
                    await context.send("Restored, brother.")
                else:
                    await context.send(self.failure("psql", process))
            else:
                await context.send("Attach a dump to restore, brother.")

    def run(self, command: List[str], stdin: Optional[bytes] = None) -> subprocess.CompletedProcess:
        """Runs a postgres client command against the bot's database."""
        url = self.db.db.url
        args = command + ["--host", url.host, "--username", url.username, "--dbname", url.database]
        return subprocess.run(args, input=stdin, capture_output=True, timeout=TIMEOUT, env=os.environ | {"PGPASSWORD": url.password or ""})

    def failure(self, name: str, process: subprocess.CompletedProcess) -> str:
        return f"`{name}` fell over, brother:\n```{process.stderr.decode().strip()[-1800:]}```"
