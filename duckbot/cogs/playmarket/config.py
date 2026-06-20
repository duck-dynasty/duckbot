"""Tunable game constants. Everything that decides "feel" lives here, not scattered in code.

Coins are whole integers. The economy is scaled up (a 10,000-coin start) so the market
maker's unavoidable fractional results round to whole coins with negligible loss.
"""

from datetime import timedelta

STARTING_BALANCE = 10_000  # granted each season
SEASON_LENGTH = timedelta(days=182)  # ~6 months; only used when auto-creating the next season
SETTLEMENT_GRACE = timedelta(days=7)  # window after a season ends for open markets to resolve

TOPUP_THRESHOLD = 1_000  # may claim only when balance is below this
TOPUP_TARGET = 2_000  # claiming tops balance up to this
TOPUP_COOLDOWN = timedelta(days=7)

MIN_BET = 10

LIQUIDITY = {"low": 500, "med": 1_000, "high": 2_000}  # creator's choice of `b`
