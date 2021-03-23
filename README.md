# duckbot
[![GitHub License](https://img.shields.io/github/license/chippers255/duckbot)](https://github.com/Chippers255/duckbot/blob/main/LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/chippers255/duckbot)](https://github.com/Chippers255/duckbot/issues)
[![Build Status](https://img.shields.io/github/workflow/status/Chippers255/duckbot/DuckBot%20CI)](https://github.com/Chippers255/duckbot/actions/workflows/python-package.yml)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Chippers255_duckbot&metric=code_smells)](https://sonarcloud.io/dashboard?id=Chippers255_duckbot)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=Chippers255_duckbot&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=Chippers255_duckbot)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Discord bot for personal friend group. If you don't know me personally, consider how freaking weird it'd be to ask for the access token. Feel free to steal the code though.

View the [wiki](https://github.com/Chippers255/duckbot/wiki) for a short description on what the Duck does.

## Development
DuckBot uses `python3.8`. All of the scripts expect `python3.8` to be on the `$PATH`.  
Scripts should be run from the repository root. When run from elsewhere, you may get moved to the repository root.

The `scripts/` directory contains scripts for development.

### Install Dependencies
Should be run whenever you pull from `upstream/main`.
```sh
. scripts/build/install.sh
```

### Run Tests, Formatter and Linter
```sh
. scripts/build/test.sh
. scripts/build/format.sh
. scripts/build/lint.sh
```

The `test` script also performs code coverage checks. [View the script](https://github.com/Chippers255/duckbot/blob/main/scripts/build/test.sh) to see the minimum required coverage. Discord.py decorators make it difficult to cover methods directly, so don't aim for 100% coverage.

#### Containerized Tests
If you like containers, you can also run all the tests as part of a docker image build. If the docker image is built, all the tests passed. The script deletes the image afterwards, pass or fail. Requires `docker` to be on the `$PATH`.
```sh
. scripts/build/docker-test.sh
```

### Run DuckBot
Requires `duckbut/.env` to be present, and the `DISCORD_TOKEN` environment variable to be set therein. The process will be killed after an hour.
```
. scripts/duckbot.sh
```

The `duckbot/.env` file should look something like this:
```
duck@pond$ cat duckbot/.env
DISCORD_TOKEN=thesecrettoken
```
