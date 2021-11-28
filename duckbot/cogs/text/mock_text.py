from discord.ext import commands

from duckbot.util.messages import get_message_reference, try_delete


class MockText(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mock")
    async def mock_text_command(self, context: commands.Context, *, text: str = ""):
        await self.mock_text(context, text)

    async def mock_text(self, context, text: str):
        if text == "":
            mocked_text = await self.mockify(f"{context.message.author.display_name}, based on this, I should mock you... I need text dude.")
        else:
            mocked_text = await self.mockify(text.strip())
        reply = await get_message_reference(context.message)
        if reply:
            await reply.reply(mocked_text)
        else:
            await context.send(mocked_text)

    async def mockify(self, text: str):
        counter = 0
        char_list = []
        for char in text.lower():
            if char.isalpha():
                if counter % 2 == 0:
                    char = char.upper()
                counter += 1
            char_list.append(char)
        return "".join(char_list)

    @mock_text_command.after_invoke
    async def delete_command_message(self, context: commands.Context):
        await try_delete(context.message)
