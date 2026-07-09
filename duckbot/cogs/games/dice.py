from typing import Optional

import d20
from discord.ext import commands

from duckbot.util.messages import MAX_MESSAGE_LENGTH

CRIT_HIT_FLAVOUR = ":dart: **Critical hit!**"
CRIT_FAIL_FLAVOUR = ":skull: **Critical fail!**"


class Dice(commands.Cog):
    @commands.hybrid_command(name="roll", aliases=["r"], description="Roll some Dungeons & Dragons style dice!")
    async def roll(self, context: commands.Context, *, expression: str = "1d20"):
        """
        :param expression: The number and type of dice to roll. Default is 1d20
        """
        max_length = MAX_MESSAGE_LENGTH - 50  # max-50 as a buffer for the added text
        try:
            roller = self.make_roller(100_000)
            result = roller.roll(expression, allow_comments=True, stringifier=DiceStringifier())
            text = f"{result.result[:max_length]}..." if len(result.result) > max_length else result.result
            response = f"**Rolls**: {text}\n**Total**: {result.total}"
            flavour = self._crit_flavour(result.expr)
            if flavour:
                response = f"{flavour}\n{response}"
            await context.send(response)
        except d20.errors.TooManyRolls:
            await context.send(f"I can only roll up to {roller.context.max_rolls} dice.", delete_after=30)
        except d20.errors.RollError as e:
            await context.send(f"Oh... :nauseated_face: I don't feel so good... :face_vomiting:\n```{e}```", delete_after=30)

    def make_roller(self, max_rolls: int):
        return d20.Roller(d20.RollContext(max_rolls))

    @staticmethod
    def _crit_flavour(expr) -> Optional[str]:
        stack = [expr]
        while stack:
            node = stack.pop()
            if isinstance(node, d20.Dice) and node.size == 20:
                if node.num != 1:
                    return None
                if node.values[0].total == 20:
                    return CRIT_HIT_FLAVOUR
                if node.values[0].total == 1:
                    return CRIT_FAIL_FLAVOUR
                return None
            stack.extend(node.children)
        return None


class DiceStringifier(d20.MarkdownStringifier):
    def _str_expression(self, node):
        """Default is 'f"{self._stringify(node.roll)} = `{int(node.total)}`"' -- we'll add the total ourselves."""
        return self._stringify(node.roll)
