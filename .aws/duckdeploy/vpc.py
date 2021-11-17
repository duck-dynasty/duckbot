from aws_cdk import core, aws_ec2


class Vpc(core.Construct):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id)

        # default vpc construction creates subnets in two availability zones
        self._vpc = aws_ec2.Vpc(self, "Vpc", cidr="10.0.0.0/16", enable_dns_support=True, enable_dns_hostnames=True)
        self.vpc.node.default_child.override_logical_id("Vpc")

    @property
    def vpc(self) -> aws_ec2.Vpc:
        return self._vpc
