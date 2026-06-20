"""LMSR (Logarithmic Market Scoring Rule) math. Pure functions in floats, no bot/db imports."""

import math


def subsidy(b: float) -> float:
    """House subsidy for a binary market: its max possible loss."""
    return b * math.log(2)


def cost(q_yes: float, q_no: float, b: float) -> float:
    """LMSR cost function, computed log-sum-exp style to avoid overflow."""
    high = max(q_yes, q_no)
    return high + b * math.log(math.exp((q_yes - high) / b) + math.exp((q_no - high) / b))


def price_yes(q_yes: float, q_no: float, b: float) -> float:
    """Instantaneous YES price (implied probability)."""
    high = max(q_yes, q_no)
    yes = math.exp((q_yes - high) / b)
    no = math.exp((q_no - high) / b)
    return yes / (yes + no)


def shares_for_budget(q_yes: float, q_no: float, b: float, side: str, budget: float) -> float:
    """Net new `side` shares a coin `budget` buys; the closed-form inverse of `cost`."""
    other = (q_no - q_yes) if side == "yes" else (q_yes - q_no)
    ratio = math.exp(other / b)
    return b * math.log((1 + ratio) * math.exp(budget / b) - ratio)
