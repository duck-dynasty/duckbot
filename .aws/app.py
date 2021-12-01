import json
import os
from typing import List

import boto3
from aws_cdk import core
from duckdeploy.secret import Secret
from duckdeploy.stack import DuckBotStack

SECRETS = [
    Secret(environment_name="DISCORD_TOKEN", parameter_name="/duckbot/token/discord"),
    Secret(environment_name="OPENWEATHER_TOKEN", parameter_name="/duckbot/token/openweather"),
    Secret(environment_name="BOT_GITHUB_TOKEN", parameter_name="/duckbot/token/github"),
    Secret(environment_name="WOLFRAM_ALPHA_TOKEN", parameter_name="/duckbot/token/wolfram-alpha"),
    Secret(environment_name="OXFORD_DICTIONARY_ID", parameter_name="/duckbot/token/oxford-dictionary/id"),
    Secret(environment_name="OXFORD_DICTIONARY_KEY", parameter_name="/duckbot/token/oxford-dictionary/key"),
]


def validate_secrets_present_in_environment(secrets: List[Secret]):
    missing_values = [x.environment_name for x in secrets if not os.getenv(x.environment_name)]
    if missing_values:
        raise EnvironmentError(f"missing environment values for secrets: {missing_values}")


def publish_secrets(secrets: List[Secret]):
    validate_secrets_present_in_environment(secrets)
    ssm_client = boto3.client("ssm")
    for s in secrets:
        ssm_client.put_parameter(Name=s.parameter_name, Value=os.getenv(s.environment_name), Type="SecureString", Overwrite=True)


if __name__ == "__main__":
    app = core.App()

    write_secrets = app.node.try_get_context("write_secrets")
    if write_secrets and json.loads(write_secrets.lower()):
        publish_secrets(SECRETS)

    DuckBotStack(app, "duckbot", secrets=SECRETS)
    app.synth()
