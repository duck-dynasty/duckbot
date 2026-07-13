# CLAUDE.md

## Project Overview

DuckBot is a Discord bot built with discord.py, written in Python 3.13. It uses a Cog-based architecture where each feature is a separate module under `duckbot/cogs/`.

## Development Setup

```sh
python3.13 -m venv --clear --prompt duckbot venv
. venv/bin/activate
pip install --editable .[dev]
setup_nltk
```

## Common Commands

- **Run tests**: `pytest` (includes tests, lint, and format checks; runs in parallel via pytest-xdist)
- **Run formatter**: `format` (reformats entire codebase using black + isort)
- **Run with coverage**: `pytest --cov=duckbot --cov-branch --cov-report term-missing:skip-covered`
- **Run the bot**: `python -m duckbot` (requires DISCORD_TOKEN env var at minimum)
- **Run with database**: `docker-compose up --build`
- **Run without docker**: `run_local` (SQLite file instead of Postgres; loads `.env` itself)

## Project Structure

- `duckbot/` — main package
  - `cogs/` — feature modules (each subdirectory is a Cog auto-loaded at startup)
  - `slash/` — slash command handlers
  - `db/` — database models (SQLAlchemy + PostgreSQL via psycopg2)
  - `health/` — health check endpoint
  - `logs/` — logging configuration
  - `util/` — shared utilities
- `tests/` — mirrors `duckbot/` structure; uses pytest with pytest-asyncio
- `scripts/` — CLI entry points (declared in `pyproject.toml` `[project.scripts]`)
- `.aws/` — CDK deployment (AWS ECS); see `.aws/CLAUDE.md`
- `wiki/` — end-user docs (how to use the bot's commands/events from Discord), not developer docs

**Reuse shared helpers before writing your own.** `duckbot/util/` holds one concern per subpackage — currently `users`, `embeds`, `datetime`, `emojis`, `messages` (e.g. `util.users.get_user`, `util.embeds.group_by_max_length` are the most-reinvented). Read the module for its current API rather than trusting a signature listed here.

## Code Style

- **Formatter**: black (line length 200, target py313)
- **Import sorting**: isort (black-compatible profile)
- **Linter**: flake8 (max line length 200, max complexity 10)
- Unused imports in `__init__.py` files are allowed (F401 ignored)
- **Comments are terse.** One short line is plenty — the first sentence is enough detail. Don't write multi-line explainer docstrings, restate what the code already says, or narrate the "why" at length. Reviewers reject verbose, AI-style comments; prefer self-documenting code with the occasional one-liner for genuinely non-obvious things.

## Cog Conventions

- **When a cog exposes multiple related commands, group them under one `@commands.hybrid_group`** (see `weather`, `games/satisfy`) — e.g. `/market bet`, `/market balance` — rather than adding many top-level commands to the global namespace. A group isn't required for a cog with a single command, and many cogs have no commands at all (pure event listeners).
- **Admin/owner checks**: reuse the owner-id allowlist pattern from `duckbot/cogs/github/yolo_merge.py` (`is_repository_admin`) instead of inventing new permission logic.
- **Prefer the simplest design that works.** Fewer moving parts, fewer places things happen. Avoid speculative complexity (schedulers, multi-step flows, extra tables/state) when a simpler approach fits a small friend-group bot. Study how existing cogs solve a similar problem and match that before introducing a new pattern.

### Adding a New Cog

- Each subdirectory of `duckbot/cogs/` is auto-loaded at startup — `duckbot/__main__.py` walks `pkgutil.iter_modules` and loads every package (dir with an `__init__.py`).
- The package `__init__.py` must expose `async def setup(bot)` that calls `bot.add_cog(...)`. Simplest example: `duckbot/cogs/ai/__init__.py`. One `setup` may register several cogs (see `duckbot/cogs/corrections/__init__.py`).
- The Cog class lives in a sibling module and subclasses `commands.Cog`. It may be command-driven (`@commands.hybrid_group`/`hybrid_command`, see `playmarket`) or event-only (`@commands.Cog.listener`, see `duckbot/cogs/corrections/`) — no commands required.
- Mirror the source path in tests: `tests/cogs/<name>/<name>_test.py`, with fixtures defined inline (see Testing Conventions).

## Database & Migrations

- `duckbot.db.Database` is a singleton. DB cogs receive it from their `setup`, which passes `Database()` into the constructor (see `duckbot/cogs/playmarket/__init__.py`, `duckbot/cogs/weather/__init__.py`) and store it as `self.db`.
- Usage: `with self.db.session(SomeModel) as session:` then `session.commit()`. `session(model)` lazily runs `model.metadata.create_all` before returning, so tables are created on first use. Canonical example: `PlayMarket.tick` in `duckbot/cogs/playmarket/market.py`.
- **Testing the DB** (reinforces "Don't shadow shared fixtures" below): the global `db` fixture is a *mocked* session; use `in_memory_db` (real in-memory SQLite, `tests/fixtures/database.py`) when logic is worth testing against real rows.
- **Migrations** use Alembic (`alembic.ini` at repo root). Versioned files live in `duckbot/db/migrations/versions/` named `00N_description.py` (e.g. `003_playmarket.py`). They run at startup only when `RUN_MIGRATIONS` is set (`duckbot/__main__.py` → `Database().migrate()`). Since `metadata.create_all` handles fresh tables in dev/tests, migrations are for schema changes to already-deployed tables.

## Testing Conventions

- Tests use pytest with `asyncio_mode = "auto"` — async test functions work without explicit markers.

- Tests run in parallel (`-n auto --dist loadfile`) with network access blocked (`--blockage`).

- Global fixtures are in `tests/fixtures/` and loaded via `tests/conftest.py`. The `message` fixture generates multiple test cases (guild channel, DM, group channel).

- **Cog-specific fixtures and helpers live in the test file**, not a per-cog `conftest.py` — there are no per-cog conftests in this repo. Even cogs with many test files (e.g. `games/satisfy`) define their fixtures inline; duplicating a one-line `cog`/`clazz` fixture across files is fine and preferred over a shared conftest. Only put genuinely reusable, behaviour-agnostic fixtures in `tests/fixtures/`.

- **Don't shadow shared fixtures.** The global `db` fixture is a *mocked* session. For logic worth testing against real rows (balances, ledgers, etc.), use the shared `in_memory_db` fixture (real in-memory SQLite, in `tests/fixtures/database.py`) — don't redefine `db` locally.

- To test a `@commands.command` / `@commands.hybrid_command` (or a group subcommand), wire the cog's commands in the fixture with `bind_commands` (`tests/discord_test_ext.py`) so `Command.__call__` injects `self`, then call the command by name:

  ```python
  # source
  class Foo(commands.Cog):
      @commands.hybrid_command(name="foo")
      async def foo(self, context): ...


  # test
  from tests.discord_test_ext import bind_commands


  @pytest.fixture
  def clazz(bot) -> Foo:
      return bind_commands(Foo(bot))


  async def test_foo(clazz, context):
      await clazz.foo(context)
  ```

  `bind_commands` walks nested group subcommands too, so `/foo bar` is `await clazz.bar(context)`.

- A `@tasks.loop` isn't a `Command`, so delegate its body to a plain method and test that:

  ```python
  @tasks.loop(hours=1)
  async def foo_loop(self):
      await self.foo()


  async def foo(self): ...  # test: await clazz.foo()
  ```

### Mocking Patterns

- **Mock imported functions at the import location**, not where they're defined:
  ```python
  # If your_module.py has: from discord.utils import utcnow
  # Then patch: "duckbot.cogs.your_module.your_module.utcnow"
  @mock.patch("duckbot.cogs.touch_grass.touch_grass.utcnow")
  async def test_something(mock_utcnow, bot, message):
      mock_utcnow.return_value = datetime.datetime(
          2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc
      )
  ```
  See examples: `tests/cogs/insights/insights_test.py`, `tests/cogs/github/yolo_merge_test.py`
- **Multiple patches**: Stack decorators; parameters appear in reverse order:
  ```python
  @mock.patch("random.choice")
  @mock.patch("module.utcnow")
  async def test(mock_utcnow, mock_random):  # reversed!
      ...
  ```

### Fixture Usage

- **`message` fixture**: Parametrized across channel types (text_channel, dm_channel, group_channel, thread). Each test using this fixture runs 4 times automatically.

- **`raw_message` fixture**: Bare mock with no properties set. Use when you need custom setup that differs from defaults.

- **`bot` fixture**: Mocked DuckBot instance. Use `bot.user` for the bot's author.

- **Mutating fixtures is allowed**: You can set properties directly on fixtures:

  ```python
  message.author.id = 12345
  message.author.display_name = "TestUser"
  ```

- Don't aim for 100% coverage — some discord.py decorators (e.g. `@tasks.loop`, autocomplete/error handlers) still make certain methods hard to cover directly.

## Pull Requests

- **Open PRs against `duck-dynasty/duckbot`** (`main`) — this is usually a fork, so don't target the fork.
- **Fill out the PR template** (`.github/pull_request_template.md`): a summary of what/why, and the checklist (tick the source-change items you actually did — `format`, `pytest`, link the fixed issue with a _fixes_ keyword, update the wiki if needed).
- **Start the PR title with a [gitmoji](https://gitmoji.dev/) shortcode** in `:code:` form (e.g. `:bug:`, `:art:`, `:arrow_up:`) — PRs squash-merge, so the title becomes the commit message. Title by the mechanism / what changed, not the symptom.

## Environment Variables

Only `DISCORD_TOKEN` is required. Other optional tokens: `OPENWEATHER_TOKEN`, `BOT_GITHUB_TOKEN`, `WOLFRAM_ALPHA_TOKEN`, `WORDNIK_KEY`, `GROQ_API_KEY`. These live in `duckbot/.env` (used when running the bot directly / via the VS Code launch config) or the repo-root `.env` (read by `docker-compose`). Neither is committed.
