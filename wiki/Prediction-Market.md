DuckBot runs a toy prediction market with play-money coins. Bet on whether group-relevant questions ("Will Sam finish the marathon under 4h?") come true, watch the odds move as people trade, and climb the seasonal leaderboard. It's all play coins — no real money, no crypto, just rows in a database.

Prices are set by an automated market maker (an LMSR — see [How prices work](#how-prices-work)), so there's always someone to trade with and the YES % is a live read on what the group believes.

## Quick start

> Human: /market create question:"Will it rain Saturday?" rules:"Per the NWS forecast at 6pm Friday" closes:"in 2 days"\
> DuckBot: Market **7** open: _Will it rain Saturday?_ — YES 50%. Closes 2025-07-01 18:00.\
> Human: /market bet market_id:7 side:yes amount:500\
> DuckBot: Bought 832 YES shares for 500 coins. YES is now 70%.

After a market closes, anyone can propose the outcome; if nobody disputes it within 24 hours, it resolves and winners get paid.

## Command overview

|                 Command                  | Summary                                           |
| :--------------------------------------: | ------------------------------------------------- |
|            `/market balance`             | show your coins, locked bonds, and open positions |
|             `/market claim`              | claim the need-based top-up if you're broke       |
|          `/market leaderboard`           | current-season standings by net worth             |
|             `/market season`             | show the active season and your rank              |
|  [`/market create`](#creating-a-market)  | open a new YES/NO market                          |
|         `/market list [status]`          | list markets and their current YES %              |
|              `/market show`              | show one market and your position in it           |
|       [`/market quote`](#betting)        | preview a bet without placing it                  |
|        [`/market bet`](#betting)         | buy YES or NO shares for a coin budget            |
|        [`/market sell`](#betting)        | sell shares back to the market                    |
| [`/market propose`](#resolving-a-market) | propose the outcome of a closed market            |
| [`/market dispute`](#resolving-a-market) | challenge a proposed outcome                      |
| [`/market resolve`](#resolving-a-market) | _(admins)_ settle a disputed market               |

Every command works as both a slash command (`/market bet`) and a prefix command (`!market bet`), but slash is recommended — `side`, `outcome`, and `liquidity` come with pick-lists.

## Coins and seasons

Everyone starts each **season** with **10,000 coins**. A season lasts about six months, after which balances reset and a fresh leaderboard begins — so a cold streak is never permanent and everyone re-levels.

- Coins are always **whole numbers**. (Share counts can be fractional under the hood — that's the market's internal accounting — but you bet and get paid in whole coins.)
- Coins are spent placing bets and posting bonds, and earned when your bets pay out.
- If you go broke (under 1,000 coins) **and** hold no open positions, `/market claim` tops you back up to 2,000 coins, once per week. It's the only faucet, so balances still track skill within a season.
- At season end there's a 7-day grace period for open markets to resolve, then balances reset and the final standings are recorded in a hall of fame.

Use `/market balance` to see your coins and positions, `/market leaderboard` for the standings (ranked by net worth = coins + the live value of your open positions), and `/market season` for how much time is left and where you rank.

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

You can sell any shares you hold back to the market at any time before it closes, locking in a gain or cutting a loss. You can't sell shares you don't own; to bet the other way, buy the opposite side.

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
/market create question:<text> rules:<text> closes:<when> liquidity:<low|med|high>
```

- **question** — the YES/NO question, e.g. _"Will the deploy go out before Friday?"_

- **rules** — the fine print that decides the payout. Be specific: this is what proposers and disputers will argue over. e.g. _"YES if a release tag is pushed to main before 2025-07-04 00:00 UTC."_

- **closes** — when trading stops. Accepts natural input like `in 3 days`, `in 6 hours`, `in 2 weeks`, or an absolute `2025-07-01 18:00`. Must be before the season ends.

- **liquidity** — how deep the market is (defaults to `med`):

  | Tier   | `b`   | Price sensitivity        | House subsidy |
  | ------ | ----- | ------------------------ | ------------- |
  | `low`  | 500   | swings hard per bet      | ~346 coins    |
  | `med`  | 1,000 | a ~600-coin bet ≈ 20 pts | ~693 coins    |
  | `high` | 2,000 | barely budges per bet    | ~1,386 coins  |

Anyone can create a market; the house funds the subsidy, so it costs you nothing.

## Betting

```
/market quote market_id:<n> side:<yes|no> amount:<coins>   ← preview only, no coins spent
/market bet   market_id:<n> side:<yes|no> amount:<coins>
/market sell  market_id:<n> side:<yes|no> shares:<number|all>
```

- **quote** shows how many shares your budget buys and where the price would land — handy before committing.
- **bet** spends `amount` coins buying shares of the side you pick, at the live price.
- **sell** returns shares to the market for coins. Pass `all` to dump your whole position on that side.

The minimum bet is 10 coins. You can only trade while a market is **open** (before its close time).

## Resolving a market

Once a market passes its close time it stops trading and waits to be resolved. Resolution is permissionless — you don't need an admin for the normal case.

```
/market propose market_id:<n> outcome:<yes|no>
/market dispute market_id:<n>
/market resolve market_id:<n> outcome:<yes|no|void>   ← admins only
```

1. **Propose** — anyone calls `/market propose` with the outcome and posts a **500-coin bond**. The market enters a 24-hour dispute window.
1. **Undisputed** — if nobody disputes within 24 hours, the outcome is accepted, the proposer gets their bond back, and winners are paid (1 coin per winning share).
1. **Dispute** — if someone thinks the proposal is wrong, they call `/market dispute` and post a matching 500-coin bond. The market is now **disputed** and needs an admin.
1. **Admin ruling** — an admin (the bot owner, or anyone with **Manage Server**) calls `/market resolve` with the true outcome. The side that was right gets their bond back **plus** the other's bond; the side that was wrong forfeits theirs. Then winners are paid.

**Void.** If a question becomes unanswerable, an admin can resolve it `void`: every share — YES and NO — redeems at 0.5 coins, and all bonds are returned. Nobody wins, nobody gets robbed.

Holders of winning positions are motivated to propose so they get paid, so markets tend to resolve themselves. If a market is still unresolved when the season's grace period ends, it's automatically voided so no coins get stranded.

## Economy at a glance

| Thing                  | Value                                                    |
| ---------------------- | -------------------------------------------------------- |
| Starting balance       | 10,000 coins per season                                  |
| Season length          | ~6 months, then balances reset                           |
| Need-based top-up      | under 1,000 coins & no positions → back to 2,000, weekly |
| Minimum bet            | 10 coins                                                 |
| Propose / dispute bond | 500 coins each                                           |
| Dispute window         | 24 hours                                                 |
| Trading fee            | 0% — the house funds the markets                         |
| Liquidity tiers        | low `b=500`, med `b=1,000`, high `b=2,000`               |
