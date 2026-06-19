# PRD — Toy Prediction Market for Discord ("PlayMarket")

**Status:** Draft v3
**Owner:** (you)
**Audience:** ~10-person Discord server, ~4–5 active traders
**Money:** Play coins only. No real money, no crypto. Coins are rows in Postgres.
**Form factor:** A new DuckBot cog at `duckbot/cogs/playmarket/`. No changes to existing cogs or core; this PRD is additive.

**Changes in v3:** Rewrote all implementation sections to fit the existing DuckBot codebase (discord.py + SQLAlchemy + the `Database` singleton + Alembic + `tasks.loop`). The economy design (§3) and LMSR math (§4–§5) are unchanged. New §15 maps everything onto DuckBot's conventions; new §16 covers testing.

**Changes in v2 (retained):** Added a **seasons** model (default 6 months, configurable) as the primary inflation control, with end-of-season settlement, balance reset, and an archived leaderboard. Replaced the universal weekly stipend with a **need-based top-up** so balances stay meaningful within a season.

______________________________________________________________________

## 1. Summary

A DuckBot cog that runs a toy prediction market. Members get play coins and can:

- **Create** a YES/NO market on any future question with a close date.
- **Bet** by buying YES or NO shares at live, automatically-priced odds.
- **Sell** shares back at any time before close to lock in gains or cut losses.
- **Resolve** a market after its close date through a propose-and-dispute flow.

Pricing uses a **Logarithmic Market Scoring Rule (LMSR)** automated market maker. This is the standard prediction-market AMM: it always has liquidity (no need for a matching counterparty), produces a clean probability for each outcome, and supports buying and selling at any time. There is no order book and nothing blockchain-related.

This is an **additive** feature. It reuses DuckBot's existing Postgres database (the `Database` singleton at `duckbot/db/database.py`), discord.py command system, and `tasks.loop` background-job pattern. No new infrastructure and no new required environment variables.

______________________________________________________________________

## 2. Goals & non-goals

**Goals**

- Fun, low-friction betting on group-relevant questions ("Will Sam finish the marathon under 4h?").
- Live odds that visibly move when people trade — the core source of fun in a small group.
- Anyone can create and anyone can resolve; no central operator required for the happy path.
- Provably solvent play economy: the bot can never owe coins it cannot pay.
- **Drop cleanly into DuckBot**: one self-contained cog, auto-loaded like every other cog, using existing DB and command conventions.

**Non-goals**

- Real money, withdrawals, KYC, or crypto.
- Order books, limit orders, or partial-fill matching.
- Multi-outcome markets at launch (binary YES/NO only; see §13 for future work).
- High-frequency or adversarial trading defenses beyond basic integrity.
- Any change to DuckBot's core, existing cogs, or deployment (the cog rides the existing ECS/docker-compose deploy unchanged).

______________________________________________________________________

## 3. Economy design (proposed numbers)

Tuned for ~10 members with ~4–5 active. Rationale follows each number.

| Parameter                        | Value                                                                                         | Why                                                                                                                             |
| -------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Starting balance (per season)    | **1,000 coins**                                                                               | Reset to this each season. Round, generous enough for many bets, small enough that losses sting a little.                       |
| Season length                    | **6 months** (configurable; see §11)                                                          | Bounds long-term inflation and periodically re-levels the playing field. One-line change to make it longer/shorter.             |
| Settlement grace period          | **7 days** after season end                                                                   | Lets still-open markets resolve before the reset; no coins get stranded.                                                        |
| Need-based top-up                | If balance **< 100** and **no open positions**: claim back up to **200 coins**, once per week | The *only* faucet. Keeps wiped-out players in the game without showering everyone, so within-season balances still track skill. |
| Default liquidity `b`            | **100**                                                                                       | A ~60-coin bet moves the price ~20 points — meaningful and visible with few traders, without being wild.                        |
| Liquidity tiers (creator choice) | Low `b=50`, Med `b=100`, High `b=200`                                                         | Higher `b` = deeper book, smaller price swings per bet, larger house subsidy.                                                   |
| Min bet                          | **1 coin**                                                                                    | Low barrier.                                                                                                                    |
| Propose bond                     | **50 coins**                                                                                  | Enough to deter frivolous/false proposals; recoverable.                                                                         |
| Dispute bond                     | **50 coins** (must match)                                                                     | Symmetric stake on the challenger.                                                                                              |
| Trading fee                      | **0%**                                                                                        | Keep it simple and fun; the house funds liquidity (see §4.5).                                                                   |
| Dispute window                   | **24 hours** after a proposal                                                                 | Long enough for the group to notice, short enough to settle fast.                                                               |

Constants live in a single module-level config in the cog (e.g. `duckbot/cogs/playmarket/config.py`) so they are easy to tune. Nothing here needs an environment variable.

**Inflation control.** Seasons cap long-term coin growth (the supply resets every 6 months), and the need-based top-up is the only recurring source of new coins — it only pays players who are actually broke, so it injects a trickle rather than a flood. Together these keep raw balance a fair proxy for trading skill, both for the live leaderboard and the end-of-season standings.

**Who funds liquidity:** The **house (the bot) funds each market's subsidy**, not the creator. This makes market creation free and risk-free, which is required for "anyone can create." The house's per-market exposure is bounded (see §4.4) and small (≤ ~139 coins even at the High tier). Coins are just DB rows, so the house can always cover its bounded obligations.

______________________________________________________________________

## 4. Market mechanism & math (LMSR)

Each market has two outcomes, **YES** and **NO**. The AMM tracks the net number of shares of each outcome that have been bought:

- `q_yes` = net YES shares outstanding
- `q_no` = net NO shares outstanding

Both start at `0`. A winning share is redeemable for exactly **1 coin** at resolution; a losing share is worth **0**.

> **Implementation note.** All the math below is pure Python (`math.exp`, `math.log`) and belongs in a dependency-free module, e.g. `duckbot/cogs/playmarket/lmsr.py`. Keeping it pure means it can be unit-tested directly without the bot or the database (see §16). Use Python `Decimal` for stored quantities (mapped to SQLAlchemy `Numeric(20,6)`), converting to `float` only inside the LMSR helpers.

### 4.1 Cost function

The state of the market is summarized by a single cost function:

```
C(q_yes, q_no) = b * ln( exp(q_yes / b) + exp(q_no / b) )
```

`b > 0` is the liquidity parameter. Larger `b` means prices move less per share traded (deeper liquidity) and a larger house subsidy.

### 4.2 Price (implied probability)

The instantaneous price of each outcome is the partial derivative of `C`, which conveniently is just a softmax:

```
price_yes = exp(q_yes / b) / ( exp(q_yes / b) + exp(q_no / b) )
price_no  = 1 - price_yes
```

`price_yes` is always in (0, 1) and is displayed to users as the market's "YES %". At launch (`q_yes = q_no = 0`) it is exactly 0.50.

### 4.3 Buying and selling

A trade changes one of the quantities and the trader pays (or receives) the **change in `C`**.

**Buy `Δ` shares of YES** (Δ > 0) costs:

```
cost = C(q_yes + Δ, q_no) - C(q_yes, q_no)
```

**Buy `Δ` shares of NO** costs `C(q_yes, q_no + Δ) - C(q_yes, q_no)`.

**Sell** `x` shares you hold = buy `-x`: the "cost" comes out negative, i.e. the trader is paid:

```
proceeds = C(q_yes, q_no) - C(q_yes - x, q_no)     // selling x YES shares
```

Selling is only permitted down to the number of shares the user actually holds (no shorting; to bet the other way, buy the opposite outcome).

### 4.4 Buy by coin budget (the UX primitive)

Users will say "**bet 50 coins on YES**" rather than picking a share count. Invert the cost function to find how many shares `Δ` a budget `X` buys. Let `a = exp(q_yes/b)` and `c = exp(q_no/b)`.

**Shares of YES for budget `X`:**

```
Δ_yes = b * ln( ( (a + c) * exp(X / b) - c ) / a )
```

**Shares of NO for budget `X`:**

```
Δ_no  = b * ln( ( (a + c) * exp(X / b) - a ) / c )
```

These are exact closed forms — no numerical solver needed.

> **Numerical note.** `exp(q/b)` can overflow `float` for large `q/b`. Implement `C` and the softmax with the standard log-sum-exp / max-subtraction trick (`m = max(q_yes, q_no); C = m + b*ln(exp((q_yes-m)/b) + exp((q_no-m)/b))`). At this game's scale (`b ≥ 50`, modest `q`) overflow is unlikely, but the guard is cheap and worth a unit test.

### 4.5 House subsidy & solvency (why this is safe)

The house pre-funds each market with a **subsidy** equal to the LMSR's maximum possible loss. For a binary market that is:

```
subsidy = b * ln(2)        // ≈ 0.6931 * b
```

So Low `b=50` → ~35 coins, Med `b=100` → ~69 coins, High `b=200` → ~139 coins.

**Solvency guarantee.** At any time, the pool of coins available to pay out equals:

```
pool = subsidy + (net coins traders have paid in)
     = C(0,0) + [ C(q_yes, q_no) - C(0,0) ]
     = C(q_yes, q_no)
```

The payout owed at resolution is the number of winning shares, which is either `q_yes` or `q_no`. Because

```
C(q_yes, q_no) >= max(q_yes, q_no)
```

the pool always covers the payout, with leftover `C - q_winner ≥ 0` returning to the house. **The bot can never become insolvent.**

**House P&L** for a resolved market is `C(q_final) - payout - subsidy`, bounded below by `-b·ln(2)`. With two-sided trading the house often comes out *ahead*; in lopsided markets it pays out up to the subsidy. Over many markets this nets to a mild, bounded coin faucet that rewards accurate traders — exactly the dynamic we want.

> The "house" is a bookkeeping concept, not a user row — house funding/leftovers are simply `ledger` rows with `user_id = NULL` and `reason = subsidy`. No real Discord user backs the house.

### 4.6 Rounding & precision

- Store `q_yes`, `q_no`, balances, and share holdings as SQLAlchemy `Numeric(20,6)` (Postgres `NUMERIC`), not integers, to keep LMSR math exact. Read/write them as Python `Decimal`.
- Display coins and shares rounded to whole numbers (or 1 decimal) in Discord.
- When rounding *is* applied to a charged amount, **round buy costs up** and **sell proceeds down** (house's favor) so accumulated rounding can never break the solvency guarantee.

______________________________________________________________________

## 5. Worked example (`b = 100`)

Start: `q_yes = q_no = 0`, YES price = **50%**.

1. **Alice bets 50 coins on YES.**
   `a = c = 1`. `Δ_yes = 100·ln((2·e^0.5 − 1)/1) ≈ 83.2` shares.
   New state: `q_yes = 83.2`, `q_no = 0` → YES price ≈ **69.7%**. Alice holds 83.2 YES.

1. **Bob thinks that's too high, bets 50 coins on NO.**
   `a = e^0.832 ≈ 2.298`, `c = 1`. `Δ_no = 100·ln((3.298·e^0.5 − 2.298)/1) ≈ 114.4` shares.
   New state: `q_yes = 83.2`, `q_no = 114.4` → YES price ≈ **42.3%**. Bob holds 114.4 NO.

1. **Market resolves YES.**

   - Alice's 83.2 YES shares pay **83.2 coins** → profit **+33.2** on her 50-coin bet.
   - Bob's NO shares pay **0** → loss **−50**.
   - Pool = `C(83.2, 114.4) ≈ 169.3`. Subsidy was `100·ln2 ≈ 69.3`; traders paid in `≈ 100`.
   - Payout 83.2 ≤ pool 169.3. House P&L = `169.3 − 83.2 − 69.3 = +16.8`.

   Had it resolved **NO**: Bob's 114.4 shares pay 114.4 (profit +64.4), Alice loses 50, house P&L = `169.3 − 114.4 − 69.3 = −14.4` (within the −69.3 bound).

These exact numbers make good unit-test fixtures for `lmsr.py` (§16).

______________________________________________________________________

## 6. Market lifecycle (state machine)

```
        create                close_at reached            propose (after close)
 (none) ───────► OPEN ──────────────────────► CLOSED ───────────────────────► PROPOSED
                  │  trading                     │ no trading                     │
                  │  buy / sell                  │                                │
                  └──────────────────────────────                                │
                                                                                  │
                              ┌──────────── no dispute within 24h ───────────────┤
                              ▼                                                   │
                          RESOLVED  ◄──── admin decides ──── DISPUTED ◄── dispute ┘
                         (payouts run)
```

| State      | Meaning                               | Allowed actions               |
| ---------- | ------------------------------------- | ----------------------------- |
| `OPEN`     | Before close date                     | buy, sell, view               |
| `CLOSED`   | Past close date, awaiting resolution  | propose, view                 |
| `PROPOSED` | Outcome proposed, dispute window open | dispute, view                 |
| `DISPUTED` | Challenged, awaiting admin ruling     | admin resolve                 |
| `RESOLVED` | Final                                 | view, redeem (auto)           |
| `VOID`     | Cancelled/ambiguous                   | view, refund (auto, see §8.3) |

State transitions that fire on time (not on a user action) are driven by a discord.py `@tasks.loop(minutes=1)` background task on the cog (see §15.4), which flips `OPEN → CLOSED` when `close_at` passes and finalizes `PROPOSED → RESOLVED` when a dispute window expires undisputed. The same checks also run lazily whenever a market is touched by a command, so correctness does not depend on the scheduler — the loop is just a liveness convenience.

______________________________________________________________________

## 7. Commands (discord.py hybrid commands)

DuckBot exposes user commands via discord.py `@commands.hybrid_command` / `@commands.hybrid_group`, which register as both prefix (`!`) and slash (`/`) commands and auto-sync through `duckbot/slash/sync_command_tree.py`. PlayMarket follows the same pattern — **no bespoke slash plumbing needed**.

To avoid polluting the global command namespace with generic verbs (`/bet`, `/create`, `/resolve`), all market actions live under a single `@commands.hybrid_group(name="market")`, mirroring how the weather cog groups `/weather get` and `/weather set`. The four economy-wide commands (`balance`, `claim`, `leaderboard`, `season`) stay top-level since they are not about a single market.

| Command                                                                                | Who        | Effect                                                                                 |
| -------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------- |
| `/balance`                                                                             | anyone     | Show coins, locked coins, and open positions.                                          |
| `/claim`                                                                               | anyone     | Claim the need-based top-up if eligible (balance < 100, no open positions, once/week). |
| `/leaderboard`                                                                         | anyone     | Current-season standings ranked by net worth (balance + position value).               |
| `/season`                                                                              | anyone     | Show the active season: name, time remaining, your rank.                               |
| `/market create question:<text> rules:<text> closes:<when> liquidity:<low\|med\|high>` | anyone     | Create an `OPEN` market in the active season; house locks the subsidy.                 |
| `/market list [status]`                                                                | anyone     | List markets with current YES %.                                                       |
| `/market show id:<n>`                                                                  | anyone     | Show one market: question, rules, YES %, your position, volume.                        |
| `/market bet id:<n> side:<yes\|no> amount:<coins>`                                     | anyone     | Buy shares for a coin budget at the live price (§4.4).                                 |
| `/market sell id:<n> side:<yes\|no> shares:<n\|all>`                                   | anyone     | Sell held shares back to the AMM.                                                      |
| `/market quote id:<n> side:<yes\|no> amount:<coins>`                                   | anyone     | Preview shares & resulting price without trading.                                      |
| `/market propose id:<n> outcome:<yes\|no>`                                             | anyone     | Post 50-coin bond, move market to `PROPOSED`.                                          |
| `/market dispute id:<n>`                                                               | anyone     | Post 50-coin bond, move market to `DISPUTED`.                                          |
| `/market resolve id:<n> outcome:<yes\|no\|void>`                                       | admin only | Break a dispute; run payouts.                                                          |

Conventions to follow:

- Use `discord.app_commands.Choice` for the `side`, `outcome`, and `liquidity` enums (see `duckbot/cogs/games/pokemon.py` for the `Choice` import pattern).
- Per CLAUDE.md / the existing cogs, each decorated command method should be a thin shim that delegates to a plain `async` method holding the logic, so the logic is testable without the decorator (see §16). Example:
  ```python
  @market.command(name="bet", description="Buy YES/NO shares for a coin budget.")
  async def bet_command(self, context, id: int, side: str, amount: float):
      await self.bet(context, id, side, amount)


  async def bet(
      self, context, id: int, side: str, amount: float
  ): ...  # all the real work; unit-tested directly
  ```
- `/market resolve` is gated by a `@commands.check(...)` predicate that raises `commands.MissingPermissions`, exactly like `is_repository_admin` in `duckbot/cogs/github/yolo_merge.py` (see §15.5).

`closes:<when>` accepts natural inputs like `2025-07-01 18:00` or `in 3 days`. DuckBot already vendors `dateparser` / has date utilities in `duckbot/util/datetime.py`; parse with those and store as `TIMESTAMPTZ` in the bot's configured timezone. Reject unparseable input with a friendly message.

______________________________________________________________________

## 8. Resolution & dispute flow

### 8.1 Happy path

1. After `close_at`, anyone calls `/market propose` with the outcome and posts a 50-coin bond (moved from balance to `locked`).
1. Market enters `PROPOSED`; the bot announces it with a 24h countdown.
1. If no dispute by `window_ends`: outcome is accepted, market `RESOLVED`, proposer's bond is **returned**, payouts run (§8.2). This finalization is triggered by the §15.4 loop (or lazily on next touch).

### 8.2 Payout on resolve

For the winning outcome `w ∈ {yes, no}`:

- Each holder of a winning share receives **1 coin/share**, credited to balance, logged in the ledger.
- Losing shares are zeroed.
- Leftover pool (`C(q) − payout`) and any unspent subsidy return to the house (`ledger` rows with `user_id = NULL`).
- Positions for the market are closed.

### 8.3 Void / ambiguous

If a market is voided (admin `/market resolve … void`, or a question that became unanswerable): **every YES and every NO share redeems at 0.5 coins.** This is always solvent because `0.5·(q_yes+q_no) ≤ max(q_yes,q_no) ≤ C(q_yes,q_no)`. Bonds are returned.

### 8.4 Dispute path

1. During `PROPOSED`, anyone calls `/market dispute` and posts a matching 50-coin bond → state `DISPUTED`.
1. An **admin** calls `/market resolve` with the true outcome (or `void`).
1. Bond settlement (zero-sum, no coins minted):
   - If the **proposer** was right → proposer gets their bond back **plus the disputer's** bond.
   - If the **disputer** was right → disputer gets their bond back **plus the proposer's** bond.
   - If `void` → both bonds returned.
1. Payouts then run per §8.2 / §8.3.

Only one active proposal per market; the first `/market propose` locks it. No reward is needed to motivate proposing — holders of winning positions are already incentivized to resolve so they get paid — but an optional small flat proposer reward can be added later if proposing lags.

______________________________________________________________________

## 9. Data model (SQLAlchemy + Postgres)

DuckBot defines tables as SQLAlchemy ORM models (see `duckbot/cogs/weather/saved_location.py`), and the `Database.session(model)` helper auto-creates the table for a model's metadata on first use (`item_type.metadata.create_all(self.db)`). **All PlayMarket models must share one `declarative_base()`** so a single `self.db.session(AnyPlayMarketModel)` call creates the whole schema and so cross-table work happens in one session. Put the shared `Base` and all models in `duckbot/cogs/playmarket/models.py`.

```python
# duckbot/cogs/playmarket/models.py
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()  # ONE base shared by every model below


class Season(Base):
    __tablename__ = "pm_seasons"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)  # "Season 1"
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(
        DateTime(timezone=True), nullable=False
    )  # duration lives here, not in code
    status = Column(
        String, nullable=False, default="active"
    )  # active|settling|archived
    starting_balance = Column(Numeric(20, 6), nullable=False, default=1000)


class PlayerAccount(Base):
    __tablename__ = "pm_users"
    id = Column(BigInteger, primary_key=True)  # discord user id (NOT autoincrement)
    balance = Column(Numeric(20, 6), nullable=False, default=0)
    locked = Column(Numeric(20, 6), nullable=False, default=0)  # bonds in flight
    last_topup_at = Column(DateTime(timezone=True), nullable=True)
    # balance + locked == SUM(ledger.delta) for this user within the active season


class Market(Base):
    __tablename__ = "pm_markets"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    season_id = Column(BigInteger, ForeignKey("pm_seasons.id"))
    creator_id = Column(BigInteger, ForeignKey("pm_users.id"))
    question = Column(String, nullable=False)
    rules = Column(String, nullable=False)  # fine print that decides payout
    b = Column(Numeric(12, 4), nullable=False)  # liquidity parameter
    subsidy = Column(Numeric(20, 6), nullable=False)  # = b*ln(2), funded by house
    q_yes = Column(Numeric(20, 6), nullable=False, default=0)
    q_no = Column(Numeric(20, 6), nullable=False, default=0)
    status = Column(
        String, nullable=False, default="OPEN"
    )  # OPEN|CLOSED|PROPOSED|DISPUTED|RESOLVED|VOID
    outcome = Column(String, nullable=True)  # 'yes'|'no'|'void' once resolved
    close_at = Column(
        DateTime(timezone=True), nullable=False
    )  # must be <= season.ends_at
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Position(Base):
    __tablename__ = "pm_positions"
    user_id = Column(BigInteger, ForeignKey("pm_users.id"), primary_key=True)
    market_id = Column(BigInteger, ForeignKey("pm_markets.id"), primary_key=True)
    yes_shares = Column(Numeric(20, 6), nullable=False, default=0)
    no_shares = Column(Numeric(20, 6), nullable=False, default=0)


class Proposal(Base):
    __tablename__ = "pm_proposals"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    market_id = Column(BigInteger, ForeignKey("pm_markets.id"))
    proposer_id = Column(BigInteger, ForeignKey("pm_users.id"))
    proposed = Column(String, nullable=False)  # 'yes'|'no'
    bond = Column(Numeric(20, 6), nullable=False)
    disputer_id = Column(BigInteger, ForeignKey("pm_users.id"), nullable=True)
    dispute_bond = Column(Numeric(20, 6), nullable=True)
    resolver_id = Column(BigInteger, nullable=True)  # admin who broke a dispute
    window_ends = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        String, nullable=False, default="pending"
    )  # pending|accepted|disputed|settled


class SeasonResult(Base):
    __tablename__ = "pm_season_results"  # final standings snapshot at close
    season_id = Column(BigInteger, ForeignKey("pm_seasons.id"), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("pm_users.id"), primary_key=True)
    final_balance = Column(Numeric(20, 6), nullable=False)
    rank = Column(Integer, nullable=False)


class LedgerEntry(Base):
    __tablename__ = "pm_ledger"  # immutable audit log; source of truth
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    season_id = Column(BigInteger, ForeignKey("pm_seasons.id"))
    user_id = Column(
        BigInteger, ForeignKey("pm_users.id"), nullable=True
    )  # NULL = the house
    market_id = Column(
        BigInteger, ForeignKey("pm_markets.id"), nullable=True
    )  # NULL for grants/top-ups
    delta = Column(Numeric(20, 6), nullable=False)  # +/- coins
    reason = Column(
        String, nullable=False
    )  # season_grant|bet|sell|payout|bond|bond_return|bond_win|subsidy|refund|topup
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
```

Notes on fitting DuckBot:

- **Table prefix `pm_`** keeps these from ever colliding with other cogs' tables in the shared `duckbot` database.
- **`pm_users.id` is the raw Discord user id** (a `BIGINT` primary key, *not* autoincrement) — same as how `weather_locations.id` stores `context.author.id`.
- The original PRD's raw SQL (`BIGSERIAL`, `DEFAULT now()`) maps directly: `BIGSERIAL → BigInteger primary_key autoincrement`, `now() → server/Python default`, `NUMERIC(20,6) → Numeric(20,6)`.

**Integrity rule:** `pm_users.balance`/`locked` are cached running totals. Every change is written with a matching `pm_ledger` row in the same session/transaction, scoped to the active season. For any user, `balance + locked` must equal `SUM(ledger.delta)` over the **current season** (the `season_grant` row of +1,000 at season start makes this reconcile from zero). A periodic check (run from the §15.4 loop, or a `/market` admin subcommand) asserts it. A season reset is therefore not a destructive edit — it is just a new `season_grant` row under a new `season_id`, leaving prior seasons' ledgers intact for audit.

### 9.1 Schema creation & migrations

Two compatible paths exist in this repo; do **both** for parity with `weather`:

1. **Runtime auto-create (works out of the box).** Because every model shares one `Base`, the first `self.db.session(Season)` call runs `Base.metadata.create_all(self.db)`, creating all `pm_*` tables if absent. This requires no migration and is enough for a fresh deploy.

1. **Alembic migration (recommended, matches weather).** Add `duckbot/db/migrations/versions/003_playmarket.py` (revision after `002_drop_city_id`) with `op.create_table(...)` for each `pm_*` table, plus useful indexes (`pm_markets(status)`, `pm_markets(season_id)`, `pm_ledger(season_id, user_id)`, `pm_positions(market_id)`). Migrations run on container start when `RUN_MIGRATIONS=true` (set in the Dockerfile) via `Database().migrate()` in `duckbot/__main__.py`.

   For Alembic autogenerate to *see* the new tables, `duckbot/db/migrations/env.py` currently sets `target_metadata = Base.metadata` from the weather model only. Combine both metadatas, e.g.:

   ```python
   from duckbot.cogs.weather.saved_location import Base as WeatherBase
   from duckbot.cogs.playmarket.models import Base as PlayMarketBase

   target_metadata = [WeatherBase.metadata, PlayMarketBase.metadata]
   ```

   (Hand-writing the `003_playmarket.py` revision is fine too and avoids touching `env.py` — but updating `env.py` keeps future autogenerate honest.)

______________________________________________________________________

## 10. Concurrency & integrity

Every state-changing command runs inside a single SQLAlchemy session/transaction obtained from the `Database` singleton. The session is created with `self.db.session(<any pm model>)`; use it as a context manager and `commit()` once at the end (rollback on exception):

```python
with self.db.session(Market) as session:
    market = (
        session.query(Market).filter_by(id=market_id).with_for_update().one()
    )  # row lock
    account = session.query(PlayerAccount).filter_by(id=user_id).with_for_update().one()
    # re-check market.status and account.balance AFTER acquiring the locks
    # compute LMSR cost (lmsr.py), update q_*, balance/locked, Position, append LedgerEntry rows
    session.commit()
```

1. `.with_for_update()` on the affected `pm_markets` row (and the acting `pm_users` row) to serialize concurrent trades on the same market — the SQLAlchemy equivalent of the PRD's `SELECT … FOR UPDATE`.
1. Re-check state and balance **after** acquiring the lock (guards against two simultaneous bets overspending or trading a just-closed market).
1. Compute LMSR cost, update `q_*`, `balance`/`locked`, `pm_positions`, and append `pm_ledger` row(s) — all on the same session.
1. `commit()`. On any exception the `with` block / explicit `try` rolls back — no partial state.

> The `Database.session()` helper returns a plain `Session` (no autobegin wrapper), so wrap the body in `try/except: session.rollback(); raise` to guarantee atomic rollback, since several writes happen per command.

**Idempotency:** Discord can deliver a double-tap. Guard with the Discord interaction id where available, or a short-lived in-memory de-dupe / a unique key on a recent-action table, so a double-tap can't double-bet. (discord.py hybrid commands expose `context.interaction` for slash invocations.)

______________________________________________________________________

## 11. Seasons

Seasons are the primary inflation control and the way the game stays fresh. Each season is a fixed window after which balances reset and a new leaderboard begins.

### 11.1 Configuration

A season's length lives entirely in the `pm_seasons` row (`starts_at`, `ends_at`), not in code. A single default constant `SEASON_LENGTH = 6 months` (in `playmarket/config.py`) is used **only** when auto-creating the next season; you can override it per season by writing whatever `ends_at` you want. So changing the cadence later — 3 months, 12 months, a one-off short test season — is a one-line change or a single row edit, with no logic changes.

### 11.2 Market–season binding

Every market belongs to exactly one season (`pm_markets.season_id`). At creation, the bot rejects a `close_at` later than the active season's `ends_at`, so every market is guaranteed resolvable before the season closes. New markets can only be created while a season is `active`.

### 11.3 Season end & settlement

When `now()` passes `ends_at`, the season moves `active → settling` and the **7-day grace period** begins:

- No new markets; no new trading (all markets are at/after their close by construction).
- `/market propose`, `/market dispute`, and `/market resolve` still work, so open markets can finish normally.
- Selling is frozen along with all other trading; positions are unwound only through market resolution (or the force-void below).

At the end of the grace period, any market still not `RESOLVED` is **force-voided** (every share redeems at 0.5 coins per §8.3), so no coins are ever stranded in an unresolved market across the boundary.

The season state transitions (`active → settling → archived`) are driven by the same `@tasks.loop` as market timing (§15.4); they also run lazily when any command touches the active season.

### 11.4 Reset & rollover

Once all markets are settled/voided and the grace period ends, the season moves `settling → archived` in a single session/transaction that:

1. Computes each player's final net worth (by now just `balance`, since positions are closed) and writes `pm_season_results` with ranks.
1. Creates the next `pm_seasons` row (`status='active'`, `ends_at = starts_at + SEASON_LENGTH`).
1. For every member, writes a `season_grant` ledger row of `+starting_balance` under the **new** `season_id` and sets `balance = starting_balance`, `locked = 0`.

Prior seasons' ledger rows are never deleted, so the full history stays auditable.

> **Bootstrap:** there is no season on first deploy. On cog load (or first command), if no `active` season exists, create "Season 1" with `ends_at = now + SEASON_LENGTH`. Players are lazily created on first interaction (their `season_grant` of +1,000 is written the first time they touch the bot in a season), mirroring how the weather cog upserts a user row on first use rather than pre-seeding all members.

### 11.5 Leaderboard & hall of fame

- **Live:** `/leaderboard` ranks players by net worth = `balance + current value of open positions` (value a YES share at `price_yes`, a NO share at `price_no`). Because everyone started the season at 1,000 and the only faucet is the small need-based top-up, this is a fair measure of in-season skill.
- **Archived:** `pm_season_results` is the permanent record. Optionally surface a cosmetic title/role for past champions; no coin carryover, so a new season is always a level start.

______________________________________________________________________

## 12. Edge cases

- **Insufficient balance** → reject before any state change.
- **Sell more than held** → reject (or, if `all`, clamp to holdings).
- **Trade after close** → reject; suggest `/market propose`.
- **Propose before close** → reject.
- **Second proposal while one is pending** → reject; show the active one.
- **Dispute after window** → reject; the market auto-finalizes to the proposal.
- **Self-dispute** (proposer disputes own proposal) → reject.
- **Creator deletes/leaves Discord** → market is unaffected; resolution is permissionless. (Positions key on the raw Discord id, which survives a leave.)
- **No one proposes a closed market** → stays `CLOSED`; coins stay locked in positions until someone proposes. The need-based top-up keeps broke players liquid; if a market is still open at season end it is force-voided in settlement (§11.3), and an admin can `/market resolve` directly any time.
- **Tiny rounding drift** → absorbed by the subsidy buffer and the round-toward-house policy (§4.6).
- **Command used in a DM** → market commands assume a guild context for the leaderboard/season; decide whether to allow DMs or raise `commands.NoPrivateMessage()` like `yolo_merge` does (recommend: allow, since the economy is global, but `/leaderboard` is most useful in-channel).

______________________________________________________________________

## 13. Future work (post-launch)

- Multi-outcome markets (generalize `C` to `b·ln(Σ exp(qᵢ/b))`, subsidy `b·ln(n)`).
- Optional small trading fee routed to market creators if you want creator incentives.
- Cross-season cosmetic progression (titles, badges) on top of the per-season reset.
- Limit-style "alert me at X%" notifications.
- A read-only web dashboard of live markets and the season leaderboard (DuckBot already runs a small `duckbot/health/` HTTP endpoint that could host this).

______________________________________________________________________

## 14. Open questions

1. Settlement grace period — is 7 days enough for your group to get stragglers resolved, or should it be longer?
1. Need-based top-up thresholds — claim below 100, restore to 200, once/week: tune to taste once you see how often people go broke.
1. Who are the admins for `/market resolve` and for kicking off a season rollover if the auto-job is paused? See §15.5 for how this is implemented (`commands.check`) — current options are bot owner + a hardcoded id allowlist (the `yolo_merge` pattern), or checking Discord guild "Manage Server" permissions. (Propose: server owner + one trusted mod.)
1. Should markets have a max bet or position cap to stop one whale from dominating thin markets? (Probably not needed at 10 players; revisit if it gets gamey.)
1. First season start date and a name scheme ("Season 1", or themed names?).
1. Command surface — group everything under `/market <verb>` (this PRD's choice, avoids generic global command names), or keep flat top-level commands as in v2? Group is recommended.

______________________________________________________________________

## 15. Implementation in DuckBot (how it slots into the repo)

This section maps the feature onto DuckBot's actual conventions so it can be built without inventing new patterns.

### 15.1 Cog package layout

DuckBot auto-loads every package under `duckbot/cogs/` (`__main__.py` iterates `pkgutil.iter_modules(duckbot.cogs.__path__)` and calls each package's `setup(bot)`). Add:

```
duckbot/cogs/playmarket/
  __init__.py          # async def setup(bot): await bot.add_cog(PlayMarket(bot, Database()))
  playmarket.py        # the Cog: hybrid_group + commands + the tasks.loop
  models.py            # shared Base + all pm_* SQLAlchemy models (§9)
  lmsr.py              # pure LMSR math (§4) — no bot/db imports
  config.py            # tunable constants (§3, §11.1): STARTING_BALANCE, SEASON_LENGTH, BONDS, B tiers, etc.
  service.py           # (optional) DB/transaction logic separated from Discord plumbing
```

`__init__.py` follows the weather cog exactly — inject the `Database()` singleton:

```python
async def setup(bot):
    from duckbot.db import Database
    from .playmarket import PlayMarket

    await bot.add_cog(PlayMarket(bot, Database()))
```

No edit to `__main__.py` is required — the cog is discovered automatically.

### 15.2 The Cog class

```python
class PlayMarket(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db
        self.tick_loop.start()

    def cog_unload(self):
        self.tick_loop.cancel()
```

(Constructor injection of `bot` + `db`, loop started in `__init__`, cancelled in `cog_unload` — identical to `announce_day` / `insights`.)

### 15.3 Slash command registration

Nothing special: hybrid commands defined on the cog are auto-synced by the existing `SyncCommandTree` cog (`duckbot/slash/sync_command_tree.py`) on `on_ready`. In non-prod (`AppConfig.is_production()` is false) it also syncs per-guild for fast iteration. PlayMarket gets this for free.

### 15.4 Background timing job

A single `@tasks.loop(minutes=1)` on the cog handles all time-driven transitions:

```python
@tasks.loop(minutes=1)
async def tick_loop(self):
    await self.tick()  # OPEN→CLOSED, PROPOSED→RESOLVED, season active→settling→archived, force-void


@tick_loop.before_loop
async def before_tick(self):
    await self.bot.wait_until_ready()
```

This mirrors `insights.py` (`before_loop` waits for ready) and `announce_day.py`. Because every command also runs these checks lazily on the rows it touches, the loop is a convenience, not a correctness dependency (§6).

### 15.5 Admin gate for `/market resolve`

Reuse the `yolo_merge` pattern — a `commands.check` predicate that raises on failure:

```python
async def is_market_admin(context: commands.Context):
    if context.guild is None:
        raise commands.NoPrivateMessage()
    if (
        not await context.bot.is_owner(context.author)
        and not context.author.guild_permissions.manage_guild
    ):
        raise commands.MissingPermissions(["manage server"])
    return True


@market.command(name="resolve")
@commands.check(is_market_admin)
async def resolve_command(self, context, id: int, outcome: str):
    await self.resolve(context, id, outcome)
```

Using `guild_permissions.manage_guild` (rather than a hardcoded id list) keeps the admin set in Discord; swap to the hardcoded-id approach from `yolo_merge` if you prefer an explicit allowlist (Open Q #3).

### 15.6 Config / secrets

**No new environment variables.** The DB is already configured (`Database` hardwires the `duckbot:pond@postgres/duckbot` engine, overridable via `DATABASE_URL` for migrations). Game constants live in `playmarket/config.py`, not env. Admin ids (if you choose the allowlist route) can be a constant or read via `os.getenv` like other optional tokens.

### 15.7 Dependencies

LMSR math needs only Python stdlib `math` and `decimal`. Date parsing for `closes:` should reuse `duckbot/util/datetime.py` (and any date library already in `pyproject.toml`) rather than adding a new dependency. No new packages expected.

______________________________________________________________________

## 16. Testing (matches DuckBot conventions)

Tests mirror the source tree under `tests/cogs/playmarket/` and run under the existing `pytest` setup (`asyncio_mode = "auto"`, parallel via xdist, network blocked). Follow the patterns in CLAUDE.md and existing tests:

- **`tests/cogs/playmarket/setup_test.py`** — assert `setup(bot)` adds the `PlayMarket` cog (like every cog's `setup_test.py`).
- **`tests/cogs/playmarket/lmsr_test.py`** — pure-function tests for `lmsr.py` using the §5 worked example as fixtures (cost, price, buy-by-budget inversion, sell proceeds, subsidy = `b·ln2`, solvency inequality, overflow guard). No mocks needed — this is the highest-value, easiest-to-cover surface.
- **`tests/cogs/playmarket/playmarket_test.py`** — command-logic tests. Per CLAUDE.md, test the delegate methods (`self.bet`, `self.resolve`, …) directly, not the decorated `*_command` shims. Use the existing `bot`, `context`, `message`, and `db`/`session` fixtures (`tests/fixtures/database.py` already provides a mocked `db` whose `session(...)` context manager yields a mock `session`).
- **`cog_unload` test** — assert `tick_loop.cancel()` is called (see `announce_day_test.py::test_cog_unload_cancels_task`).
- **`before_loop` test** — assert it awaits `bot.wait_until_ready()` (see `announce_day_test.py`).
- **Time-dependent logic** (season end, dispute window, close_at) — patch the time source. Patch at the import location per CLAUDE.md, e.g. `duckbot.cogs.playmarket.playmarket.now` (mirroring `@mock.patch("duckbot.util.datetime.now", ...)` in `announce_day_test.py`). Import `now`/`utcnow` into the cog module and patch there.
- Don't chase 100% coverage — the `@commands.hybrid_command`/`@tasks.loop` decorators make the shim methods hard to invoke directly; covering the delegate methods + `lmsr.py` is the goal.

> Because real DB transactions/`with_for_update` are hard to exercise against the mocked session, keep the money-moving + LMSR logic in plain methods (`service.py` / cog delegate methods) that take values in and return deltas out, so they can be unit-tested with the mocked `session`, while the actual locking/commit lives in a thin wrapper that's exercised lightly. This separation also makes the §10 integrity invariant testable in isolation.
