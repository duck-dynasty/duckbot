from aws_cdk import core
from .vpc import Vpc
from .service import Service
from .hosts import Hosts


class DuckBotStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        vpc = Vpc(self, "Vpc").vpc
        auto_scaling_group = Hosts(self, "Hosts", vpc=vpc).auto_scaling_group

        Service(self, "Service", vpc=vpc, auto_scaling_group=auto_scaling_group)
