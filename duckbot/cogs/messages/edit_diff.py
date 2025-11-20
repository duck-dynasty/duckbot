import re
from difflib import ndiff

from discord.ext import commands
from nltk import edit_distance


class EditDiff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.edit_threshold = 6
        self.delete_after_seconds = 120

    @commands.Cog.listener("on_message_edit")
    async def show_edit_diff(self, before, after):
        if self.should_send_diff(before, after):
            msg = ""
            prev = " "  # start out as no change
            for d in ndiff(self.split_words(before.clean_content), self.split_words(after.clean_content)):
                change = d[0]
                if change != "?":  # ignore stuff not in either message
                    msg += self.try_leave_diff_chunk(change, prev)
                    msg += self.try_enter_diff_chunk(change, prev)
                    msg += d[2:]  # append the letter
                    prev = change
            msg += self.try_leave_diff_chunk(" ", prev)  # close the final diff chunk if necessary
            await after.channel.send(f":eyes: {after.author.mention}.\n{msg}", delete_after=self.delete_after_seconds)

    def should_send_diff(self, before, after):
        return (
            before.author != self.bot.user
            and after.author != self.bot.user
            and before.content != after.content
            and (before.author.id == 244629273191645184 or after.author.id == 244629273191645184 or edit_distance(before.clean_content, after.clean_content) > self.edit_threshold)
        )

    def split_words(self, content):
        return re.split(r"(\s+)", content)

    def try_leave_diff_chunk(self, change, prev):
        if change != prev and prev != " ":
            return prev + ("}" if prev == "+" else "]")
        else:
            return ""

    def try_enter_diff_chunk(self, change, prev):
        if change != prev and change != " ":
            return ("{" if change == "+" else "[") + change
        else:
            return ""
