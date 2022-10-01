from typing import List

from aws_cdk import aws_autoscaling, aws_ec2, aws_ecs, aws_efs, aws_logs, aws_ssm, core

from .secret import Secret


class DuckBotStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, *, secrets: List[Secret]):
        super().__init__(scope, construct_id)

        vpc = aws_ec2.Vpc(
            self,
            "Vpc",
            enable_dns_support=True,
            enable_dns_hostnames=True,
            max_azs=3,
            nat_gateways=0,
            subnet_configuration=[aws_ec2.SubnetConfiguration(name="Public", subnet_type=aws_ec2.SubnetType.PUBLIC)],
        )

        postgres_volume_name = "duckbot_dbdata"
        file_system = aws_efs.FileSystem(self, "PostgresFileSystem", vpc=vpc, encrypted=True, file_system_name=postgres_volume_name, removal_policy=core.RemovalPolicy.DESTROY)
        file_system.node.default_child.override_logical_id("FileSystem")  # rename for compatibility with legacy cloudformation template

        task_definition = aws_ecs.TaskDefinition(self, "TaskDefinition", compatibility=aws_ecs.Compatibility.EC2, family="duckbot", memory_mib="450", network_mode=aws_ecs.NetworkMode.BRIDGE)

        postgres_data_path = "/data/postgres"
        postgres = task_definition.add_container(
            "postgres",
            container_name="postgres",
            image=aws_ecs.ContainerImage.from_registry("postgres:13.2"),
            essential=False,
            environment={
                "POSTGRES_USER": "duckbot",
                "POSTGRES_PASSWORD": "pond",
                "PGDATA": postgres_data_path,
            },
            health_check=aws_ecs.HealthCheck(
                command=["CMD", "pg_isready", "-U", "duckbot"],
                interval=core.Duration.seconds(30),
                timeout=core.Duration.seconds(5),
                retries=3,
                start_period=core.Duration.seconds(30),
            ),
            logging=aws_ecs.LogDriver.aws_logs(stream_prefix="ecs", log_retention=aws_logs.RetentionDays.ONE_MONTH),
            memory_reservation_mib=128,
        )
        task_definition.add_volume(name=postgres_volume_name, efs_volume_configuration=aws_ecs.EfsVolumeConfiguration(file_system_id=file_system.file_system_id, root_directory="/"))
        postgres.add_mount_points(aws_ecs.MountPoint(source_volume=postgres_volume_name, container_path=postgres_data_path, read_only=False))

        secrets_as_parameters = {
            # note, parameter version is required by cdk, but does not make it into the template; specify version 1 for simplicity
            x.environment_name: aws_ssm.StringParameter.from_secure_string_parameter_attributes(self, x.environment_name, parameter_name=x.parameter_name, version=1)
            for x in secrets
        }
        duckbot = task_definition.add_container(
            "duckbot",
            container_name="duckbot",
            essential=True,
            image=aws_ecs.ContainerImage.from_registry(self.node.try_get_context("duckbot_image")),
            environment={"STAGE": "prod"},
            secrets={k: aws_ecs.Secret.from_ssm_parameter(v) for k, v in secrets_as_parameters.items()},
            health_check=aws_ecs.HealthCheck(
                command=["CMD", "python", "-m", "duckbot.health"],
                interval=core.Duration.seconds(30),
                timeout=core.Duration.seconds(10),
                retries=3,
                start_period=core.Duration.seconds(30),
            ),
            logging=aws_ecs.LogDriver.aws_logs(stream_prefix="ecs", log_retention=aws_logs.RetentionDays.ONE_MONTH),
            memory_reservation_mib=128,
        )
        duckbot.add_link(postgres)

        asg = aws_autoscaling.AutoScalingGroup(
            self,
            "AutoScalingGroup",
            min_capacity=0,
            max_capacity=1,
            desired_capacity=1,
            machine_image=aws_ecs.EcsOptimizedImage.amazon_linux2(),
            instance_type=aws_ec2.InstanceType.of(instance_class=aws_ec2.InstanceClass.T3, instance_size=aws_ec2.InstanceSize.NANO),
            key_name="duckbot",  # needs to be created manually
            instance_monitoring=aws_autoscaling.Monitoring.BASIC,
            vpc=vpc,
        )

        asg.connections.allow_to_default_port(file_system)
        asg.connections.allow_from(aws_ec2.Peer.any_ipv4(), aws_ec2.Port.tcp(22))
        asg.connections.allow_from(aws_ec2.Peer.any_ipv4(), aws_ec2.Port.tcp(80))
        asg.connections.allow_from(aws_ec2.Peer.any_ipv4(), aws_ec2.Port.tcp(443))

        cluster = aws_ecs.Cluster(self, "Cluster", cluster_name="duckbot", vpc=vpc)
        cluster.add_asg_capacity_provider(aws_ecs.AsgCapacityProvider(cluster, "AsgCapacityProvider", auto_scaling_group=asg), can_containers_access_instance_role=True)

        aws_ecs.Ec2Service(
            self,
            "Service",
            service_name="duckbot",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            min_healthy_percent=0,
            max_healthy_percent=100,
        )
