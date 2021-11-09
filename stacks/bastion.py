import os.path
from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as _iam
# from aws_cdk.aws_s3_assets import Asset

currentDirName = os.path.dirname(__file__)

# Bastion EC2 Instance configs
ec2_type = "t2.micro"
linux_ami = _ec2.AmazonLinuxImage(
  generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
  edition=_ec2.AmazonLinuxEdition.STANDARD,
  virtualization=_ec2.AmazonLinuxVirt.HVM,
  storage=_ec2.AmazonLinuxStorage.GENERAL_PURPOSE
)

class BastionStack(cdk.Stack):
  def __init__(self, scope: cdk.Construct, construct_id: str, vpc: _ec2.IVpc, sg:_ec2.ISecurityGroup, mappings, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # Instance Role and SSM Managed Policy
    _role = _iam.Role(
      self, 
      "InstanceSSM", 
      assumed_by=_iam.ServicePrincipal("ec2.amazonaws.com")
    )
    _role.add_managed_policy(
      _iam.ManagedPolicy.from_aws_managed_policy_name(
        "AmazonSSMManagedInstanceCore"
      )
    )

    with open("user_data/configure_bastion_instance.sh", 'r') as user_data_h:
      # Use a substitution
      user_data_sub = cdk.Fn.sub(user_data_h.read(), mappings)

    # Import substitution object into user_data set
    _user_data = _ec2.UserData.custom(user_data_sub)

    # Create Bastion EC2 instance
    bastionInstance = _ec2.Instance(
      self, 
      "bastionInstance",
      instance_name="bastionInstance",
      vpc=vpc,
      role=_role,
      machine_image=linux_ami,
      security_group=sg,
      user_data=_user_data,
      vpc_subnets=_ec2.SubnetSelection(
        subnet_type=_ec2.SubnetType.PUBLIC,
      ),
      instance_type=_ec2.InstanceType(
        instance_type_identifier=ec2_type
      ),
    )

    # assigning our EFS resource to be able to reference it
    # across stacks
    self._bastionInstance = bastionInstance

    # output EFS resource
    cdk.CfnOutput(
      self,
      "bastionInstancePublicIpOutput",
      value=bastionInstance.instance_public_ip,
      export_name="bastionInstancePublicIp"
    )
    cdk.CfnOutput(
      self,
      "bastionInstanceIdOutput",
      value=bastionInstance.instance_id,
      export_name="bastionInstanceId"
    )

  @property
  def getInstance(self) -> _ec2.IInstance:
    return self._bastionInstance
