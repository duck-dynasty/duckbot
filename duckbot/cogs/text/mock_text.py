from discord.ext import commands


class MockText(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mock")
    async def mock_text_command(self, context, *, text: str = "Based on this, I should mock you... I need text dude."):
        await self.mock_text(context, text)

    async def mock_text(self, context, text: str):
        mocked_text = await self.mockify(text.strip())
        if len(mocked_text) < 1990:
            await context.send(f"{mocked_text}")
        else:
            mocked_text = await self.mockify("that's too much letters and stuff dude.")
            await context.send(f"{mocked_text}")

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
