DuckBot runs a toy prediction market with play-money coins. Bet on whether group-relevant questions ("Will Sam finish the marathon under 4h?") come true, watch the odds move as people trade, and climb the seasonal leaderboard. It's all play coins — no real money, no crypto, just rows in a database.

Prices are set by an automated market maker (an LMSR — see [How prices work](#how-prices-work)), so there's always someone to trade with and the YES % is a live read on what the group believes.

## Quick start

> Human: /market create question:"Will it rain Saturday?"\
> DuckBot: Market **7** open: _Will it rain Saturday?_ — YES 50%. Resolve it with `/market resolve 7 <yes|no>` when you know the outcome.\
> Human: /market bet market:7 side:yes amount:500\
> DuckBot: Bought 832 YES shares for 500 coins. YES is now 70%.

When the outcome is known, the market's creator resolves it and everyone's winning shares are paid out.

## Command overview

|                 Command                  | Summary                                             |
| :--------------------------------------: | --------------------------------------------------- |
|            `/market balance`             | show your coins and open positions                  |
|             `/market claim`              | claim the need-based top-up if you're broke         |
|          `/market leaderboard`           | current-season standings by net worth               |
|  [`/market create`](#creating-a-market)  | open a new YES/NO market                            |
|         `/market list [status]`          | list markets, their current YES % and positions     |
|        [`/market bet`](#betting)         | buy YES or NO shares for a coin budget              |
|        [`/market sell`](#betting)        | sell shares back to the market                      |
| [`/market resolve`](#resolving-a-market) | _(creator)_ resolve the market and pay everyone out |

Every command works as both a slash command (`/market bet`) and a prefix command (`!market bet`), but slash is recommended — `side`, `outcome`, and `liquidity` come with pick-lists.

## Coins and seasons

Everyone starts each **season** with **10,000 coins**. A season runs for a calendar quarter, resetting on the first day of January, April, July, and October, after which balances reset and a fresh leaderboard begins — so a cold streak is never permanent and everyone re-levels.

- Coins are always **whole numbers**. (Share counts can be fractional under the hood — that's the market's internal accounting — but you bet and get paid in whole coins.)
- Coins are spent placing bets and earned when your bets pay out.
- If you go broke (under 1,000 coins) **and** hold no open positions, `/market claim` tops you back up to 2,000 coins, once per week. It's the only faucet, so balances still track skill within a season.
- At season end there's a 7-day grace period for open markets to resolve, then balances reset and the final standings are recorded in a hall of fame.

Use `/market balance` to see your coins and positions, and `/market leaderboard` for the standings (ranked by net worth = coins + the live value of your open positions).

## How prices work

Each market tracks how many YES and NO shares have been bought. A winning share pays exactly **1 coin** when the market resolves; a losing share pays **0**. The price of a share is the market's estimate of the probability of that outcome, and it's always between 0 and 1.

DuckBot prices trades with a **Logarithmic Market Scoring Rule (LMSR)** market maker. You don't need the math to play, but here it is for the curious.

### The cost function

The whole market is summarised by one number — the cost to have reached its current state:

```
C(yes, no) = b · ln( e^(yes/b) + e^(no/b) )
```

`b` is the **liquidity** parameter chosen when the market is created. A bigger `b` means prices move less per coin traded (a "deeper" market) and a bigger house subsidy.

### Price = implied probability

The YES price is just how the cost function tilts toward YES:

```
YES price = e^(yes/b) / ( e^(yes/b) + e^(no/b) )
NO price  = 1 − YES price
```

A brand-new market has no shares on either side, so YES starts at exactly **50%**.

### Buying and selling

A trade costs the **change** in the cost function. Buying YES shares pushes the YES price up; selling them (or buying NO) pushes it back down. Because you say "bet 500 coins" rather than picking a share count, DuckBot inverts the cost function to work out how many shares 500 coins buys at the current odds — exactly, with no guessing.

You can sell any shares you hold back to the market any time before it's resolved, locking in a gain or cutting a loss. You can't sell shares you don't own; to bet the other way, buy the opposite side.

### Why the house can never go broke

When a market is created, the house (the bot) pre-funds it with a **subsidy** equal to its worst-case loss:

```
subsidy = b · ln(2)
```

That's about 346 coins for a low-liquidity market, 693 for medium, 1,386 for high. It can be shown that the pool of coins collected always covers the winning payout, no matter how lopsided the betting gets — so DuckBot can never owe coins it can't pay. Market creation is therefore free and risk-free: anyone can open one.

### A worked example

> Start: YES is 50%.\
> **Alice bets 500 coins on YES.** She gets ~832 shares; YES jumps to ~70%.\
> **Bob thinks that's too high and bets 500 coins on NO.** He gets ~1,144 shares; YES falls to ~42%.\
> **The market resolves YES.** Alice's ~832 shares pay 831 coins (a +331 profit on her 500). Bob's NO shares pay nothing (−500). The house comes out slightly ahead.

## Creating a market

```
/market create question:<text> liquidity:<low|med|high>
```

- **question** — the YES/NO question, e.g. _"Will the deploy go out before Friday?"_ Keep it clear; if the outcome's ever ambiguous, hash it out in chat.

- **liquidity** — how deep the market is (defaults to `med`):

  | Tier   | `b`   | Price sensitivity        | House subsidy |
  | ------ | ----- | ------------------------ | ------------- |
  | `low`  | 500   | swings hard per bet      | ~346 coins    |
  | `med`  | 1,000 | a ~600-coin bet ≈ 20 pts | ~693 coins    |
  | `high` | 2,000 | barely budges per bet    | ~1,386 coins  |

Anyone can create a market; the house funds the subsidy, so it costs you nothing.

## Betting

```
/market bet  market:<pick> side:<yes|no> amount:<coins>
/market sell market:<pick> side:<yes|no> shares:<number|all>
```

- **bet** spends `amount` coins buying shares of the side you pick, at the live price.
- **sell** returns shares to the market for coins. Pass `all` to dump your whole position on that side.
- **`/market balance`** shows your coins and the bets you're holding. **`/market list`** shows every open market, its current YES % and everyone's positions.

The `market` field autocompletes on slash commands — start typing and pick a market by its question, no need to look up its number first.

The minimum bet is 10 coins. You can trade right up until the market's creator resolves it.

## Resolving a market

Markets don't close on their own — the person who **created** the market settles it once the outcome is known:

```
/market resolve market:<pick> outcome:<yes|no|void>
```

- **yes / no** — every winning share is paid 1 coin; losing shares pay 0.
- **void** — if the question became unanswerable, everyone gets their stake back: whatever you spent on the market, minus anything you already took out by selling. Nobody wins, nobody gets robbed.

Everyone holding a position is pinged with the results, so you'll know how your bet went even if you miss the resolve.

Only the creator can resolve their own market — it's a friends-trust-friends "prop bet" model. If a creator never resolves (or leaves the server), the market is automatically voided when the season ends, so no coins stay stranded.

## Economy at a glance

| Thing             | Value                                                    |
| ----------------- | -------------------------------------------------------- |
| Starting balance  | 10,000 coins per season                                  |
| Season length     | 1 calendar quarter, then balances reset                  |
| Need-based top-up | under 1,000 coins & no positions → back to 2,000, weekly |
| Minimum bet       | 10 coins                                                 |
| Resolution        | by the market's creator; auto-void at season end         |
| Trading fee       | 0% — the house funds the markets                         |
| Liquidity tiers   | low `b=500`, med `b=1,000`, high `b=2,000`               |
