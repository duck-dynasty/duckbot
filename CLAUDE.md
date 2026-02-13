# CLAUDE.md

## Project Overview

DuckBot is a Discord bot built with discord.py, written in Python 3.10. It uses a Cog-based architecture where each feature is a separate module under `duckbot/cogs/`.

## Development Setup

```sh
python3.10 -m venv --clear --prompt duckbot venv
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

## Project Structure

- `duckbot/` — main package
  - `cogs/` — feature modules (each subdirectory is a Cog auto-loaded at startup)
  - `slash/` — slash command handlers
  - `db/` — database models (SQLAlchemy + PostgreSQL via psycopg2)
  - `health/` — health check endpoint
  - `logs/` — logging configuration
  - `util/` — shared utilities
- `tests/` — mirrors `duckbot/` structure; uses pytest with pytest-asyncio
- `scripts/` — CLI entry points (`format`, `setup_nltk`)
- `.aws/` — CDK deployment (AWS ECS)

## Code Style

- **Formatter**: black (line length 200, target py310)
- **Import sorting**: isort (black-compatible profile)
- **Linter**: flake8 (max line length 200, max complexity 10)
- Unused imports in `__init__.py` files are allowed (F401 ignored)

## Testing Conventions

- Tests use pytest with `asyncio_mode = "auto"` — async test functions work without explicit markers.
- Tests run in parallel (`-n auto --dist loadfile`) with network access blocked (`--blockage`).
- Global fixtures are in `tests/fixtures/` and loaded via `tests/conftest.py`. The `message` fixture generates multiple test cases (guild channel, DM, group channel).
- To test a `@commands.command` or `@tasks.loop` method, delegate the logic to a separate method and test that directly, since the decorators change the method signature:
  ```python
  # source
  class Foo(commands.Cog):
      @command(name="foo")
      async def foo_command(self, context):
          await self.foo(context)

      async def foo(self, context): ...


  # test
  async def test_foo(bot, context):
      clazz = Foo(bot)
      await clazz.foo(context)
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

- Don't aim for 100% coverage — discord.py decorators make some methods hard to cover directly.

## Environment Variables

Only `DISCORD_TOKEN` is required. Other optional tokens: `OPENWEATHER_TOKEN`, `BOT_GITHUB_TOKEN`, `WOLFRAM_ALPHA_TOKEN`, `OXFORD_DICTIONARY_ID`, `OXFORD_DICTIONARY_KEY`, `ANTHROPIC_API_KEY`. These live in `duckbot/.env` (not committed).
