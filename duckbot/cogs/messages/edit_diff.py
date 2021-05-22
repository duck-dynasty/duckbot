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
            msg += self.try_enter_diff_chunk(change, prev)
            msg += self.try_leave_diff_chunk(change, prev)
            msg += d[-1]  # append the letter
            prev = change
        msg += self.try_enter_diff_chunk(" ", prev)  # close the final diff chunk if necessary
        await after.channel.send(f":eyes: {after.author.mention}.\n{msg}", delete_after=300)

    def try_enter_diff_chunk(self, change, prev):
        if change != prev and prev != " ":
            return prev + ("}" if prev == "+" else "]")
        else:
            return ""

    def try_leave_diff_chunk(self, change, prev):
        if change != prev and change != " ":
            return ("{" if change == "+" else "[") + change
        else:
            return ""
