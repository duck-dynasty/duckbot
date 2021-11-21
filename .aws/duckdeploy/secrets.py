import json
import os
from typing import Mapping

import boto3
from aws_cdk import aws_ssm, core


class Secret(core.Construct):
    def __init__(self, scope: core.Construct, construct_id: str, *, environment_name: str, parameter_name: str):
        super().__init__(scope, construct_id)
        self._param = aws_ssm.StringParameter.from_secure_string_parameter_attributes(
            self,
            "Param",
            parameter_name=parameter_name,
            version=1,  # version is required but not actually referenced by ECS, use 1 as a dummy value
        )
        self._env = environment_name

    @property
    def parameter(self) -> aws_ssm.StringParameter:
        return self._param

    @property
    def environment_name(self) -> str:
        return self._env


class Secrets(core.Construct):
    def __init__(self, scope: core.Construct, construct_id: str):
        super().__init__(scope, construct_id)
        write_secrets_context = scope.node.try_get_context("write_secrets")
        self.write_secrets = write_secrets_context and json.loads(write_secrets_context.lower())
        self.published = False

        self._secrets = [
            Secret(self, "Discord", environment_name="DISCORD_TOKEN", parameter_name="/duckbot/token/discord"),
            Secret(self, "OpenWeather", environment_name="OPENWEATHER_TOKEN", parameter_name="/duckbot/token/openweather"),
            Secret(self, "GitHub", environment_name="GITHUB_TOKEN", parameter_name="/duckbot/token/github"),
            Secret(self, "WolframAlpha", environment_name="WOLFRAM_ALPHA_TOKEN", parameter_name="/duckbot/token/wolfram-alpha"),
            Secret(self, "OxfordDictionaryId", environment_name="OXFORD_DICTIONARY_ID", parameter_name="/duckbot/token/oxford-dictionary/id"),
            Secret(self, "OxfordDictionaryKey", environment_name="OXFORD_DICTIONARY_KEY", parameter_name="/duckbot/token/oxford-dictionary/key"),
        ]

    # FIXME implement!
    def publish(self):
        if not self.published and self.write_secrets:
            for x in self._secrets:
                print(os.environ[x.environment_name])
            ssm_client = boto3.client("ssm")

    @property
    def secrets(self) -> Mapping[str, aws_ssm.StringParameter]:
        self.publish()
        return dict((x.environment_name, x.parameter) for x in self._secrets)
