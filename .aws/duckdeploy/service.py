from aws_cdk import core, aws_ecs, aws_ec2, aws_autoscaling, aws_logs, aws_ssm
from .secrets import Secrets

class Service(core.Construct):
    def __init__(self, scope: core.Construct, construct_id: str, *, vpc: aws_ec2.IVpc, auto_scaling_group=aws_autoscaling.IAutoScalingGroup, secrets: Secrets):
        super().__init__(scope, construct_id)

        self._cluster = aws_ecs.Cluster(self, "Cluster", cluster_name="duckbot", vpc=vpc)

        asg_provider = aws_ecs.AsgCapacityProvider(self, "CapacityProvider", auto_scaling_group=auto_scaling_group)
        self.cluster.add_asg_capacity_provider(asg_provider)

        task = aws_ecs.TaskDefinition(
            self,
            "TaskDefinition",
            family="duckbot",
            memory_mib=str(960),
            network_mode=aws_ecs.NetworkMode.BRIDGE,
            compatibility=aws_ecs.Compatibility.EC2,
        )
        task.add_volume(name="duckbot_dbdata", efs_volume_configuration=aws_ecs.EfsVolumeConfiguration(file_system_id="id", root_directory="/"))

        discord_token = aws_ssm.StringParameter.from_string_parameter_attributes(self, "DiscordToken", parameter_name="/duckbot/token/discord", type=aws_ssm.ParameterType.SECURE_STRING)
        openweather_token = aws_ssm.StringParameter.from_string_parameter_attributes(self, "OpenWeatherToken", parameter_name="/duckbot/token/openweather", type=aws_ssm.ParameterType.SECURE_STRING)
        github_token = aws_ssm.StringParameter.from_string_parameter_attributes(self, "GitHubToken", parameter_name="/duckbot/token/github", type=aws_ssm.ParameterType.SECURE_STRING)
        wolfram_alpha_token = aws_ssm.StringParameter.from_string_parameter_attributes(
            self, "WolframAlphaToken", parameter_name="/duckbot/token/wolfram-alpha", type=aws_ssm.ParameterType.SECURE_STRING
        )
        oxford_dictionary_id = aws_ssm.StringParameter.from_string_parameter_attributes(
            self, "OxfordId", parameter_name="/duckbot/token/oxford-dictionary/id", type=aws_ssm.ParameterType.SECURE_STRING
        )
        oxford_dictionary_key = aws_ssm.StringParameter.from_string_parameter_attributes(
            self, "OxfordKey", parameter_name="/duckbot/token/oxford-dictionary/key", type=aws_ssm.ParameterType.SECURE_STRING
        )

        postgres = aws_ecs.ContainerDefinition(
            self,
            "postgres",
            task_definition=task,
            container_name="postgres",
            image=aws_ecs.ContainerImage.from_registry("postgres:13.2"),
            essential=False,
            memory_reservation_mib=128,
            environment={
                "POSTGRES_USER": "duckbot",
                "POSTGRES_PASSWORD": "pond",
                "PGDATA": "/data/postgres",
            },
            # health_check=aws_ecs.HealthCheck(command=["CMD", "pg_isready", "-U", "duckbot"], interval=30, timeout=5, retries=3, start_period=30),
            logging=aws_ecs.LogDriver.aws_logs(stream_prefix="ecs", log_retention=aws_logs.RetentionDays.ONE_MONTH),
        )
        postgres.add_mount_points(aws_ecs.MountPoint(source_volume="duckbot_dbdata", container_path="/data/postgres", read_only=False))
        # FIXME refer to EFS name tag

        duckbot = aws_ecs.ContainerDefinition(
            self,
            "duckbot",
            task_definition=task,
            container_name="duckbot",
            image=aws_ecs.ContainerImage.from_registry("duckbot:latest"),  # FIXME
            essential=True,
            memory_reservation_mib=128,
            secrets=dict((s.environment_name, s.parameter) for s in secrets.params),
            # health_check=aws_ecs.HealthCheck(command=["CMD", "python", "-m", "duckbot.health"], interval=30, timeout=10, retries=3, start_period=30),
            logging=aws_ecs.LogDriver.aws_logs(stream_prefix="ecs", log_retention=aws_logs.RetentionDays.ONE_MONTH),
        )
        duckbot.add_link(postgres)

    @property
    def cluster(self) -> aws_ecs.Cluster:
        return self._cluster
