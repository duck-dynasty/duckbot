# duckbot
[![GitHub License](https://img.shields.io/github/license/chippers255/duckbot)](https://github.com/Chippers255/duckbot/blob/master/LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/chippers255/duckbot)](https://github.com/Chippers255/duckbot)
[![Build Status](https://img.shields.io/github/workflow/status/Chippers255/duckbot/Python%20package)](https://github.com/Chippers255/duckbot/actions?query=workflow%3A%22Python+package%22)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Chippers255_duckbot&metric=code_smells)](https://sonarcloud.io/dashboard?id=Chippers255_duckbot)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=Chippers255_duckbot&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=Chippers255_duckbot)

A Discord bot for personal friend group. If you don't know me personally, consider how freaking weird it'd be to ask for the access token. Feel free to steal the code though.

## Development
The `scripts/build` directory contains scripts for development.

### Install Dependencies
Should be run whenever you pull from `upstream/main`.
```
. scripts/build/install.sh
```

### Run Tests and Linter
```
. scripts/build/test.sh
. scripts/build/lint.sh
```

### Run DuckBot
Requires `duckbut/.env` to be present, and the `TOKEN` environment variable to be set therein.
```
. scripts/duckbot.sh
```
