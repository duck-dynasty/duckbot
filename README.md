# duckbot
[![GitHub License](https://img.shields.io/github/license/chippers255/duckbot)](https://github.com/Chippers255/duckbot/blob/main/LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/chippers255/duckbot)](https://github.com/Chippers255/duckbot/issues)
[![Build Status](https://img.shields.io/github/workflow/status/Chippers255/duckbot/DuckBot%20CI)](https://github.com/Chippers255/duckbot/actions/workflows/python-package.yml)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Chippers255_duckbot&metric=code_smells)](https://sonarcloud.io/dashboard?id=Chippers255_duckbot)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=Chippers255_duckbot&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=Chippers255_duckbot)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A Discord bot for personal friend group. If you don't know me personally, consider how freaking weird it'd be to ask for the access token. Feel free to steal the code though.

View the [wiki](https://github.com/Chippers255/duckbot/wiki) for a short description on what the Duck does.

## Development
Before running DuckBot, you want to create a virtualenv to develop in. DuckBot runs on `python3.8`, so prefer to use that.

```sh
python3.8 -m venv --clear --prompt duckbot venv
. venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install --editable .[dev]
```

The `dev` extras will also install development dependencies, like `pytest`. The install commands should be run whenever you merge from upstream.

### Run Tests & Formatter
There are a few additional packages required to be able to run tests locally.

```sh
sudo apt-get install -y --no-install-recommends libpq-dev
```

Then, you can run tests.

```sh
pytest              # runs tests, lint and format checks
isort . && black .  # reformats the entire code base
```

The tests also collects code coverage. [View the configuration](https://github.com/Chippers255/duckbot/blob/main/pyproject.toml) to see the minimum required coverage. Discord.py decorators make it difficult to cover methods directly, so don't aim for 100% coverage.


### Run DuckBot
Before running DuckBot, you need to have a `duckbot/.env` file with the API tokens. It should look something like this:

```
duck@pond$ cat duckbot/.env
DISCORD_TOKEN=thesecrettoken
OPENWEATHER_TOKEN=thesecrettoken
```

With your tokens available, you can jam them into your environment so you can run DuckBot. You may want to put this into your bashrc for convenience.
```sh
export $(cat duckbot/.env | xargs)
```

Finally, there's two ways to run DuckBot. For a production-like environment, you should run using [docker-compose](https://docs.docker.com/compose/).
```sh
docker-compose up --build
```

If your work doesn't need a full setup, you can just run `python -m duckbot` for less wait time. Depending on what apt packages you have installed, some features may not work, see the [Dockerfile](https://github.com/Chippers255/duckbot/blob/main/Dockerfile) for what packages you'd need. For testing simple new commands though, this works fine enough.
