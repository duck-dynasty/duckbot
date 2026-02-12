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
- Don't aim for 100% coverage — discord.py decorators make some methods hard to cover directly.

## Environment Variables

Only `DISCORD_TOKEN` is required. Other optional tokens: `OPENWEATHER_TOKEN`, `BOT_GITHUB_TOKEN`, `WOLFRAM_ALPHA_TOKEN`, `OXFORD_DICTIONARY_ID`, `OXFORD_DICTIONARY_KEY`, `ANTHROPIC_API_KEY`. These live in `duckbot/.env` (not committed).
