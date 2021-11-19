from aws_cdk import core, cloudformation_include
from .vpc import Vpc
from .service import Service
from .hosts import Hosts
from .secrets import Secrets


class DuckBotStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        template = cloudformation_include.CfnInclude(self, "include", template_file="cloudformation.template.yml")

        # vpc = Vpc(self, "Vpc").vpc
        # auto_scaling_group = Hosts(self, "Hosts", vpc=vpc).auto_scaling_group
        #
        # secrets = Secrets(self, "Secrets")
        #
        # Service(self, "Service", vpc=vpc, auto_scaling_group=auto_scaling_group, secrets=secrets)
