# duckbot

[![GitHub License](https://img.shields.io/github/license/duck-dynasty/duckbot)](https://github.com/duck-dynasty/duckbot/blob/main/LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/duck-dynasty/duckbot)](https://github.com/duck-dynasty/duckbot/issues)
[![Build Status](https://img.shields.io/github/workflow/status/duck-dynasty/duckbot/DuckBot%20CI)](https://github.com/duck-dynasty/duckbot/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/duck-dynasty/duckbot/branch/main/graph/badge.svg?token=FX4DT5MWBW)](https://codecov.io/gh/duck-dynasty/duckbot)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/duck-dynasty/duckbot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/duck-dynasty/duckbot/context:python)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A Discord bot for personal friend group. If you don't know me personally, consider how freaking weird it'd be to ask for the access token. Feel free to steal the code though.

View the [wiki](https://github.com/duck-dynasty/duckbot/wiki) for a short description on what the Duck does.

https://user-images.githubusercontent.com/3149083/135654217-244d7457-9db9-4c30-a98a-785b25453fd8.mp4

## Development

Before running DuckBot, you want to create a virtualenv to develop in. DuckBot runs on `python3.8`, so prefer to use that.

```sh
python3.8 -m venv --clear --prompt duckbot venv
. venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install --editable .[dev]
```

The `dev` extras will also install development dependencies, like `pytest`. The installation commands should be run whenever you merge from upstream.

### Run Tests & Formatter

```sh
pytest  # runs tests, lint and format checks
format  # reformats the entire code base
```

You can also collect code coverage locally using:

```sh
pytest --cov=duckbot --cov-branch --cov-report term-missing:skip-covered
```

Coverage is collected in the github actions. [View the Codecov configuration](.github/.codecov.yml) to see the minimum required coverage. Discord.py decorators make it difficult to cover methods directly, so don't aim for 100% coverage.

### Run DuckBot

Before running DuckBot, you need to have a `duckbot/.env` file with the API tokens. It should look something like this:

```
duck@pond$ cat duckbot/.env
DISCORD_TOKEN=thesecrettoken
OPENWEATHER_TOKEN=thesecrettoken
GITHUB_TOKEN=somesecrettoken
WOLFRAM_ALPHA_TOKEN=broitssecret
OXFORD_DICTIONARY_ID=icanttellyou
OXFORD_DICTIONARY_KEY=itsasecret
```

- Discord tokens available from [Discord Developer](https://discord.com/developers/applications)
- You can get an [openweather api token](https://openweathermap.org/api) for free as well
- The github token is a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- The wolfram alpha token is available from their [api page](https://products.wolframalpha.com/api/)
- The oxford dictionary tokens are available from their [developer page](https://developer.oxforddictionaries.com/)

You only _need_ the discord token. DuckBot will still function without the others, but features that use the tokens won't work. With your tokens available, you can jam them into your shell environment, so you can run DuckBot. You may want to put this into your bashrc for convenience.

```sh
export $(cat duckbot/.env | xargs)
```

Finally, there are two ways to run DuckBot. For a production-like environment, you should run using [docker-compose](https://docs.docker.com/compose/). This will stand up the database alongside DuckBot.

```sh
docker-compose up --build
```

If your work doesn't need a full setup, you can just run `python -m duckbot` for less wait time. Depending on what apt packages you have installed, some features may not work, see the [Dockerfile](Dockerfile) for what packages you'd need. For testing simple new commands though, this works fine enough.

## Deployment

Deployment scripts are written using [CDK](https://docs.aws.amazon.com/cdk/latest/guide/home.html), the AWS Cloud Development Kit. The CDK dependencies can be installed alongside DuckBot.

```sh
pip install --editable .[dev,cdk]  # run from repository root
```

You'll then actually need CDK. It's a nodejs package, so you'll need that as well.

```sh
npm install -g aws-cdk
```

## Adding New Secrets

To add new secrets (like tokens), [`app.py`](.aws/app.py) needs to be modified. Add a secret to the existing list of secrets there.

- `environment_name`: the name of the environment variable in the duckbot code base; also must match the GitHub secret name which houses the actual value
- `parameter_name`: the name of the AWS Systems Manager parameter, must start with `/duckbot`

Make sure you also update the [`docker-compose`](docker-compose.yml) file, and this [readme](#run-duckbot) to include information on how developers can get their own copy of the secrets.

### Note About Secrets and Deployments

CDK is just python code at the end of the day, we take advantage of that to make sure the deployment process actually creates the secrets that DuckBot would use in prod.
In  [`app.py`](.aws/app.py), there's logic which creates the secrets via API calls, taking the value from the current environment. Those same secrets are passed to the stack, which are used to inject the secrets into the duckbot container.

Actually saving the secrets is disabled by default, but is enabled for the GitHub actions deploy step. Writing secrets can be enabled by passing `--context write_secrets=true` to a `cdk` command.

## Using CDK

You'll need AWS credentials to use CDK. The following examples assume you have those credentials saved under a `duckbot` AWS CLI profile. The `cdk` commands need to be run from the `.aws` directory.

You can also technically deploy using CDK, but should avoid that. Let the actions workflows do that.

**Synthesize a Stack**

```sh
cdk synth --profile duckbot
```

Synthesizing products `cdk.out/duckbot.template.json`, the CloudFormation template that you can deploy. It also dumps the YML version out to the console.

**Diff a Stack**

```sh
cdk diff --profile duckbot
```

Produces a diff between the stack already deployed and what you have locally.
