import random

from discord.ext import commands

from duckbot.util.messages import get_message_reference, try_delete

WRAPPERS = ["**", "*", "`"]


class MockText(commands.Cog):
    @commands.command(name="mock")
    async def mock_text_command(self, context: commands.Context, *, text: str = ""):
        await self.mock_text(context, text)

    async def mock_text(self, context: commands.Context, text: str):
        if text == "":
            mocked_text = self.mockify(f"{context.message.author.display_name}, based on this, I should mock you... I need text dude.")
        else:
            mocked_text = self.mockify(text.strip())
        reply = await get_message_reference(context.message)
        if reply:
            await reply.reply(mocked_text)
        else:
            await context.send(mocked_text)

    def mockify(self, text: str):
        counter = 0
        parts = []
        chars = list(text.lower())
        i = 0
        use_emphasis = True
        prev_wrapper = None

        while i < len(chars):
            if not chars[i].isalpha():
                parts.append(chars[i])
                i += 1
                continue

            span_len = random.randint(1, 4)
            span = []
            while i < len(chars) and chars[i].isalpha() and len(span) < span_len:
                span.append(chars[i].upper() if counter % 2 == 0 else chars[i])
                counter += 1
                i += 1

            chunk = "".join(span)
            if use_emphasis:
                wrapper = random.choice([w for w in WRAPPERS if w != prev_wrapper])
                parts.append(f"{wrapper}{chunk}{wrapper}")
                prev_wrapper = wrapper
            else:
                parts.append(chunk)

            use_emphasis = not use_emphasis

        return "".join(parts)

    @mock_text_command.after_invoke
    async def delete_command_message(self, context: commands.Context):
        await try_delete(context.message)
