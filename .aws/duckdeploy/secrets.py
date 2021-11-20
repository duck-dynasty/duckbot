from typing import List

from aws_cdk import aws_ecs, aws_ssm, core, custom_resources


# FIXME https://github.com/aws/aws-cdk/tree/master/packages/%40aws-cdk/custom-resources#get-the-latest-version-of-a-secure-ssm-parameter
class SecureStringParameter(custom_resources.AwsCustomResource, aws_ssm.IStringParameter):
    def __init__(self, scope: core.Construct, construct_id: str):
        super().__init__(
            scope,
            construct_id,
            policy=custom_resources.AwsCustomResourcePolicy.from_sdk_calls(custom_resources.AwsCustomResourcePolicy.ANY_RESOURCE()),
            on_update=custom_resources.AwsSdkCall(service="ssm", action="getParameter", parameters={"Name": "parameter-name", "WithDecryption": True}),
        )


class Secret(core.Construct):
    def __init__(self, scope: core.Construct, construct_id: str, *, environment_name: str, parameter_name: str):
        super().__init__(scope, construct_id)

        self._env_name = environment_name
        self._secret = aws_ssm.StringParameter.from_secure_string_parameter_attributes(self, parameter_name=parameter_name, version=None)

    @property
    def environment_name(self) -> str:
        return self._env_name

    @property
    def param(self):
        return self._secret


class Secrets(core.Construct):
    def __init__(self, scope: core.Construct, construct_id: str):
        super().__init__(scope, construct_id)

        self._github = Secret(self, "GitHub", environment_name="GITHUB_TOKEN", parameter_name="/duckbot/github/token")

    @property
    def params(self) -> List[Secret]:
        return [self._github]
