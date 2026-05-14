import re

import d20
from discord.ext import commands

from duckbot.util.messages import MAX_MESSAGE_LENGTH

ADVANTAGE_REPLACEMENTS = {
    "adv": "2d20kh1",
    "advantage": "2d20kh1",
    "dis": "2d20kl1",
    "disadvantage": "2d20kl1",
}
ADVANTAGE_PATTERN = re.compile(r"^\s*(advantage|adv|disadvantage|dis)\b", re.IGNORECASE)


class Dice(commands.Cog):
    @commands.hybrid_command(name="roll", aliases=["r"], description="Roll some Dungeons & Dragons style dice!")
    async def roll_command(self, context: commands.Context, *, expression: str = "1d20"):
        """
        :param expression: The number and type of dice to roll. Default is 1d20. Use `adv` or `dis` for advantage/disadvantage.
        """
        await self.roll(context, expression)

    async def roll(self, context: commands.Context, expression: str):
        expression = self._resolve_advantage(expression)
        max_length = MAX_MESSAGE_LENGTH - 50  # max-50 as a buffer for the added text
        try:
            roller = self.make_roller(100_000)
            result = roller.roll(expression, allow_comments=True, stringifier=DiceStringifier())
            text = f"{result.result[:max_length]}..." if len(result.result) > max_length else result.result
            await context.send(f"**Rolls**: {text}\n**Total**: {result.total}")
        except d20.errors.TooManyRolls:
            await context.send(f"I can only roll up to {roller.context.max_rolls} dice.", delete_after=30)
        except d20.errors.RollError as e:
            await context.send(f"Oh... :nauseated_face: I don't feel so good... :face_vomiting:\n```{e}```", delete_after=30)

    def make_roller(self, max_rolls: int):
        return d20.Roller(d20.RollContext(max_rolls))

    @staticmethod
    def _resolve_advantage(expression: str) -> str:
        """Replaces a leading `adv`/`advantage`/`dis`/`disadvantage` keyword with the equivalent dice expression."""
        return ADVANTAGE_PATTERN.sub(lambda m: ADVANTAGE_REPLACEMENTS[m.group(1).lower()], expression, count=1)


class DiceStringifier(d20.MarkdownStringifier):
    def _str_expression(self, node):
        """Default is 'f"{self._stringify(node.roll)} = `{int(node.total)}`"' -- we'll add the total ourselves."""
        return self._stringify(node.roll)
