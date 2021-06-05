from discord.ext import commands

from duckbot.util.messages import try_delete


class MockText(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mock")
    async def mock_text_command(self, context, *, text: str = ""):
        await self.mock_text(context, text)

    async def mock_text(self, context, text: str):
        if text == "":
            mocked_text = await self.mockify("based on this, I should mock you... I need text dude.")
            await context.send(f"{context.message.author.display_name}, {mocked_text}")
        elif len(text) > 1990:
            mocked_text = await self.mockify("that's too much letters and stuff dude.")
            await context.send(f"{mocked_text}")
        else:
            mocked_text = await self.mockify(text.strip())
            await context.send(f"{mocked_text}")
        await try_delete(context.message)

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
