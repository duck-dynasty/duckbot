from typing import List

from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_efs as efs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_ssm as ssm
from aws_cdk import core

from .secret import Secret


class DuckBotStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, *, secrets: List[Secret]):
        super().__init__(scope, construct_id)

        vpc = ec2.Vpc(
            self,
            "Vpc",
            enable_dns_support=True,
            enable_dns_hostnames=True,
            max_azs=3,
            nat_gateways=0,
            subnet_configuration=[ec2.SubnetConfiguration(name="Public", subnet_type=ec2.SubnetType.PUBLIC)],
        )

        postgres_volume_name = "duckbot_dbdata"
        file_system = efs.FileSystem(self, "PostgresFileSystem", vpc=vpc, encrypted=True, file_system_name=postgres_volume_name, removal_policy=core.RemovalPolicy.DESTROY)
        file_system.node.default_child.override_logical_id("FileSystem")  # rename for compatibility with legacy cloudformation template

        task_definition = ecs.TaskDefinition(self, "TaskDefinition", compatibility=ecs.Compatibility.EC2, family="duckbot", network_mode=ecs.NetworkMode.BRIDGE)

        postgres_data_path = "/data/postgres"
        postgres = task_definition.add_container(
            "postgres",
            container_name="postgres",
            image=ecs.ContainerImage.from_registry("postgres:13.2"),
            essential=False,
            environment={
                "POSTGRES_USER": "duckbot",
                "POSTGRES_PASSWORD": "pond",
                "PGDATA": postgres_data_path,
            },
            health_check=ecs.HealthCheck(
                command=["CMD", "pg_isready", "-U", "duckbot"],
                interval=core.Duration.seconds(30),
                timeout=core.Duration.seconds(5),
                retries=3,
                start_period=core.Duration.seconds(30),
            ),
            logging=ecs.LogDriver.aws_logs(stream_prefix="ecs", log_retention=logs.RetentionDays.ONE_MONTH),
            memory_reservation_mib=64,
        )
        task_definition.add_volume(name=postgres_volume_name, efs_volume_configuration=ecs.EfsVolumeConfiguration(file_system_id=file_system.file_system_id, root_directory="/"))
        postgres.add_mount_points(ecs.MountPoint(source_volume=postgres_volume_name, container_path=postgres_data_path, read_only=False))

        secrets_as_parameters = {
            # note, parameter version is required by cdk, but does not make it into the template; specify version 1 for simplicity
            x.environment_name: ssm.StringParameter.from_secure_string_parameter_attributes(self, x.environment_name, parameter_name=x.parameter_name, version=1)
            for x in secrets
        }
        duckbot = task_definition.add_container(
            "duckbot",
            container_name="duckbot",
            essential=True,
            image=ecs.ContainerImage.from_registry(self.node.try_get_context("duckbot_image")),
            environment={"STAGE": "prod"},
            secrets={k: ecs.Secret.from_ssm_parameter(v) for k, v in secrets_as_parameters.items()},
            health_check=ecs.HealthCheck(
                command=["CMD", "python", "-m", "duckbot.health"],
                interval=core.Duration.seconds(30),
                timeout=core.Duration.seconds(10),
                retries=3,
                start_period=core.Duration.seconds(30),
            ),
            logging=ecs.LogDriver.aws_logs(stream_prefix="ecs", log_retention=logs.RetentionDays.ONE_MONTH),
            memory_reservation_mib=320,
        )
        duckbot.add_link(postgres)

        launch_template = ec2.LaunchTemplate(
            self,
            "LaunchTemplate",
            block_devices=[ec2.BlockDevice(device_name="/dev/xvda", volume=ec2.BlockDeviceVolume.ebs(volume_size=8, volume_type=ec2.EbsDeviceVolumeType.GP3))],
            instance_type=ec2.InstanceType.of(instance_class=ec2.InstanceClass.T3, instance_size=ec2.InstanceSize.MICRO),
            spot_options=ec2.LaunchTemplateSpotOptions(
                max_price=0.0052,  # $0.0052 is t3.nano on-demand price
                interruption_behavior=ec2.SpotInstanceInterruption.TERMINATE,  # also release ebs volumes
            ),
            cpu_credits=ec2.CpuCredits.STANDARD,
            key_name="duckbot",  # needs to be created manually
            machine_image=ec2.MachineImage.generic_linux(ami_map={"us-east-1": "ami-0c90bcaed0062d19b"}),  # custom ECS AMI created manually via https://github.com/aws/amazon-ecs-ami
            security_group=ec2.SecurityGroup(self, "HostSecurityGroup", vpc=vpc),
            role=iam.Role(self, "HostRole", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")),
            user_data=ec2.UserData.for_linux(),
        )
        launch_template.connections.allow_to_default_port(file_system)
        launch_template.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))
        launch_template.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))
        launch_template.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(443))

        asg = autoscaling.AutoScalingGroup(
            self,
            "AutoScalingGroup",
            min_capacity=0,
            max_capacity=1,
            desired_capacity=1,
            launch_template=launch_template,
            instance_monitoring=autoscaling.Monitoring.BASIC,
            vpc=vpc,
        )

        cluster = ecs.Cluster(self, "Cluster", cluster_name="duckbot", vpc=vpc)
        cluster.add_asg_capacity_provider(ecs.AsgCapacityProvider(cluster, "AsgCapacityProvider", auto_scaling_group=asg), can_containers_access_instance_role=True)

        ecs.Ec2Service(
            self,
            "Service",
            service_name="duckbot",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            min_healthy_percent=0,
            max_healthy_percent=100,
        )
