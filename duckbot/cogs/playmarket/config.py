"""Tunable game constants. Coins are whole integers."""

from datetime import timedelta

STARTING_BALANCE = 10_000

TOPUP_THRESHOLD = 1_000
TOPUP_TARGET = 2_000
TOPUP_COOLDOWN = timedelta(days=7)

MIN_BET = 10

LIQUIDITY = {"low": 500, "med": 1_000, "high": 2_000}  # creator's choice of `b`

ADMIN_IDS = (368038054558171141, 776607982472921088, 375024417358479380)  # may resolve any market
