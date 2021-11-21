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
        write_secrets_context = self.node.try_get_context("write_secrets")
        self.write_secrets = write_secrets_context and json.loads(write_secrets_context.lower())
        self.published = False
        self._secrets = [Secret(self, s["name"], environment_name=s["environment_name"], parameter_name=s["parameter_name"]) for s in self.node.try_get_context("secrets")]

    def publish(self):
        if not self.published and self.write_secrets:
            missing_values = [x.environment_name for x in self._secrets if not os.getenv(x.environment_name)]
            if missing_values:
                raise EnvironmentError(f"missing environment values for secrets: {missing_values}")
            ssm_client = boto3.client("ssm")
            for s in self._secrets:
                print(ssm_client.get_parameter(Name=s.parameter.parameter_name, WithDecryption=True))
            self.published = True

    @property
    def secrets(self) -> Mapping[str, aws_ssm.StringParameter]:
        self.publish()
        return dict((x.environment_name, x.parameter) for x in self._secrets)
