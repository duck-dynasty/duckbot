from difflib import ndiff

from discord.ext import commands


class EditDiff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message_edit")
    async def show_edit_diff(self, before, after):
        if before.author == self.bot.user or after.author == self.bot.user or before.content == after.content:
            return

        msg = ""
        prev = " "  # start out as no change
        for d in ndiff(before.clean_content, after.clean_content):
            change = d[0]
            if change != prev and prev != " ":  # leaving a diff chunk
                msg += prev + ("}" if prev == "+" else "]")
            if change != prev and change != " ":  # entering a diff chunk
                msg += ("{" if change == "+" else "[") + change
            msg += d[-1]  # append the letter
            prev = change
        if prev != " ":  # close final diff chunk
            msg += prev + ("}" if prev == "+" else "]")
        await after.channel.send(f":eyes: {after.author.mention}.\n{msg}", delete_after=300)
