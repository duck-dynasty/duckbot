"""Tunable game constants. Everything that decides "feel" lives here, not scattered in code."""

from datetime import timedelta
from decimal import Decimal

STARTING_BALANCE = Decimal(1000)  # granted each season
SEASON_LENGTH = timedelta(days=182)  # ~6 months; only used when auto-creating the next season
SETTLEMENT_GRACE = timedelta(days=7)  # window after a season ends for open markets to resolve

TOPUP_THRESHOLD = Decimal(100)  # may claim only when balance is below this
TOPUP_TARGET = Decimal(200)  # claiming tops balance up to this
TOPUP_COOLDOWN = timedelta(days=7)

MIN_BET = Decimal(1)
PROPOSE_BOND = Decimal(50)
DISPUTE_BOND = Decimal(50)
DISPUTE_WINDOW = timedelta(hours=24)

LIQUIDITY = {"low": 50.0, "med": 100.0, "high": 200.0}  # creator's choice of `b`
