from aws_cdk import core, aws_ssm, aws_ec2, aws_autoscaling


class Hosts(core.Construct):
    def __init__(self, scope: core.Construct, construct_id: str, *, vpc: aws_ec2.IVpc):
        super().__init__(scope, construct_id)

        self._asg = aws_autoscaling.AutoScalingGroup(
            self,
            "AutoScalingGroup",
            min_capacity=0,
            max_capacity=1,
            desired_capacity=1,
            machine_image=aws_ec2.MachineImage.from_ssm_parameter("/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"),
            instance_type=aws_ec2.InstanceType("t2.micro"),
            key_name="duckbot",  # needs to be created manually
            instance_monitoring=aws_autoscaling.Monitoring.BASIC,
            vpc=vpc,
        )

    @property
    def auto_scaling_group(self) -> aws_autoscaling.AutoScalingGroup:
        return self._asg
