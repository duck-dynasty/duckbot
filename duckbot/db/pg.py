import gzip
import io
import os
import subprocess
from typing import List, Optional

import discord
from discord.ext import commands

from duckbot.util.permissions import is_repository_admin

from .database import Database


class Pg(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db

    @commands.group(name="pg")
    @commands.check(is_repository_admin)
    async def pg(self, context: commands.Context):
        pass

    @pg.command(name="dump")
    async def dump(self, context: commands.Context):
        async with context.typing():
            process = self.run(["pg_dump", "--clean", "--if-exists"])
            archive = discord.File(io.BytesIO(gzip.compress(process.stdout)), filename="duckbot.sql.gz")
            await context.author.send(file=archive)  # dumps hold everyone's saved locations, keep them out of the channel
            await context.send("Sent it to your DMs, brother.")

    @pg.command(name="restore")
    async def restore(self, context: commands.Context):
        async with context.typing():
            if context.message.attachments:
                attachment = context.message.attachments[0]
                dump = await attachment.read()
                if attachment.filename.endswith(".gz"):
                    dump = gzip.decompress(dump)
                self.run(["psql", "--variable", "ON_ERROR_STOP=1"], stdin=dump)
                await context.send("Restored, brother.")
            else:
                await context.send("Attach a dump to restore, brother.")

    @dump.error
    @restore.error
    async def on_error(self, context: commands.Context, error):
        error = getattr(error, "original", error)
        if isinstance(error, subprocess.CalledProcessError):
            await context.send(f"`{error.cmd[0]}` fell over, brother:\n```{error.stderr.decode().strip()[-1800:]}```")

    def run(self, command: List[str], stdin: Optional[bytes] = None) -> subprocess.CompletedProcess:
        """Runs a postgres client command against the bot's database, raising on failure."""
        url = self.db.db.url
        args = command + ["--host", url.host, "--username", url.username, "--dbname", url.database]
        return subprocess.run(args, input=stdin, capture_output=True, check=True, timeout=120, env=os.environ | {"PGPASSWORD": url.password or ""})
