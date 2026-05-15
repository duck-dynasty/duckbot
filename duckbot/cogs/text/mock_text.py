import random

from discord.ext import commands

import duckbot.util.messages

WRAPPERS = ["", "**", "*"]


class MockText(commands.Cog):
    @commands.command(name="mock")
    async def mock_text_command(self, context: commands.Context, *, text: str = ""):
        await self.mock_text(context, text)

    async def mock_text(self, context, text: str):
        if text == "":
            mocked_text = await self.mockify(f"{context.message.author.display_name}, based on this, I should mock you... I need text dude.")
        else:
            mocked_text = await self.mockify(text.strip())
        reply = await duckbot.util.messages.get_message_reference(context.message)
        if reply:
            await reply.reply(mocked_text)
        else:
            await context.send(mocked_text)

    async def mockify(self, text: str):
        counter = 0
        previous_was_emphasis = False
        parts = []
        for char in text.lower():
            if char.isalpha():
                if counter % 2 == 0:
                    char = char.upper()
                counter += 1
                wrapper = "" if previous_was_emphasis else random.choice(WRAPPERS)
                previous_was_emphasis = wrapper != ""
                parts.append(f"{wrapper}{char}{wrapper}")
            else:
                previous_was_emphasis = False
                parts.append(char)
        return "".join(parts)

    @mock_text_command.after_invoke
    async def delete_command_message(self, context: commands.Context):
        await duckbot.util.messages.try_delete(context.message)
