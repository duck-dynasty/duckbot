from aws_cdk import aws_autoscaling, aws_ec2, aws_ecs, aws_efs, core


class DuckBotStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # template = cloudformation_include.CfnInclude(self, "include", template_file="cloudformation.template.yml")
        vpc = aws_ec2.Vpc(
            self,
            "Vpc",
            enable_dns_support=True,
            enable_dns_hostnames=True,
            max_azs=3,
            nat_gateways=0,
            subnet_configuration=[aws_ec2.SubnetConfiguration(name="Public", subnet_type=aws_ec2.SubnetType.PUBLIC)],
        )

        file_system = aws_efs.FileSystem(self, "DatabaseFileSystem", vpc=vpc, encrypted=True, file_system_name="duckbot_dbdata", removal_policy=core.RemovalPolicy.DESTROY)
        file_system.node.default_child.override_logical_id("FileSystem")  # rename for compatibility with legacy cloudformation template

        cluster = aws_ecs.Cluster(self, "Cluster", cluster_name="duckbot", vpc=vpc)
        # service = aws_ecs.Ec2Service(self, "Service", cluster=cluster)

        # asg = aws_autoscaling.AutoScalingGroup(
        #     self,
        #     "AutoScalingGroup",
        #     min_capacity=0,
        #     max_capacity=1,
        #     desired_capacity=1,
        #     machine_image=aws_ecs.EcsOptimizedImage.amazon_linux2(),
        #     instance_type=aws_ec2.InstanceType("t2.micro"),
        #     key_name="duckbot",  # needs to be created manually
        #     instance_monitoring=aws_autoscaling.Monitoring.BASIC,
        #     vpc=vpc,
        # )
        #
        # asg.connections.allow_to(file_system, aws_ec2.Port(protocol=aws_ec2.Protocol.TCP, from_port=2049, to_port=2049, string_representation="EfsAccess"))

        # secrets = Secrets(self, "Secrets")
        #
        # Service(self, "Service", vpc=vpc, auto_scaling_group=auto_scaling_group, secrets=secrets)
