import d20
from discord.ext import commands


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll", aliases=["r"])
    async def roll_command(self, context, *, expression: str = "1d20"):
        await self.roll(context, expression)

    async def roll(self, context, expression: str):
        try:
            roller = self.make_roller(100_000)
            result = roller.roll(expression, allow_comments=True, stringifier=DiceStringifier())
            text = f"{result.result[:1950]}..." if len(result.result) > 1950 else result.result
            await context.send(f"**Rolls**: {text}\n**Total**: {result.total}")
        except d20.errors.TooManyRolls:
            await context.send(f"I can only roll up to {roller.context.max_rolls} dice.", delete_after=30)
        except d20.errors.RollError as e:
            await context.send(f"Oh... :nauseated_face: I don't feel so good... :face_vomiting:\n```{e}```", delete_after=30)

    def make_roller(self, max_rolls: int):
        return d20.Roller(d20.RollContext(max_rolls))


class DiceStringifier(d20.MarkdownStringifier):
    def _str_expression(self, node):
        """Default is 'f"{self._stringify(node.roll)} = `{int(node.total)}`"' -- we'll add the total ourselves."""
        return self._stringify(node.roll)
