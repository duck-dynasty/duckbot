from discord.ext import commands
import subprocess


class MessageModified(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message_edit")
    async def show_edit_diff(self, before, after):
        before_file = f"echo $BEFORE > {before.id}.before"
        after_file = f"echo $AFTER > {after.id}.after"
        diff_cmd = f"git diff --no-index -U10000 --word-diff=plain --word-diff-regex=. {before.id}.before {after.id}.after | tail -n +6"
        cleanup = f"rm -rf {before.id}.before {after.id}.after"
        env = {"BEFORE": before.content, "AFTER": after.content}

        process = subprocess.run(f"{before_file} && {after_file} && {diff_cmd} ; {cleanup}", shell=True, capture_output=True, env=env)
        await after.channel.send(f":eyes: {after.author.mention}.\n{process.stdout.decode()}")
