from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as _ec2

class VpcStack(cdk.Stack):
  def __init__(self, scope: cdk.Construct, construct_id: str, buildConfigs, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # reading vpc configs from the project's cdk.json context
    # TODO: check for noneness
    cidr = buildConfigs["Parameters"]["VPC"]["CIDR"]
    cidrMask = buildConfigs["Parameters"]["VPC"]["CIDRMask"]
    environment = buildConfigs["Environment"]

    # ensure high availability on production environment
    natGateways = 2 if environment == "prod" else 1

    # defining vpc subnets: public, private, and an isolated
    # subnet for our DB instances
    publicSubnetConfig = _ec2.SubnetConfiguration(
      name="publicSubnet",
      cidr_mask=cidrMask,
      subnet_type=_ec2.SubnetType.PUBLIC
    )

    privateSubnetConfig = _ec2.SubnetConfiguration(
      name="privateSubnet",
      cidr_mask=cidrMask,
      subnet_type=_ec2.SubnetType.PRIVATE
    )

    isolatedSubnetConfig = _ec2.SubnetConfiguration(
      name="isolatedSubnet",
      cidr_mask=cidrMask,
      subnet_type=_ec2.SubnetType.ISOLATED
    )

    # creating our vpc that spans over two AZs and has two
    # NAT gateways for each private subnet to achieve
    # high-availability
    _vpc = _ec2.Vpc(
      self,
      "vpc",
      cidr=cidr,
      max_azs=2,
      nat_gateways=natGateways,
      subnet_configuration=[
        publicSubnetConfig,
        privateSubnetConfig,
        isolatedSubnetConfig,
      ]
    )

    # assigning our VPC resource to be able to reference it
    # across stacks
    self._vpc = _vpc

    # our stack outputs
    cdk.CfnOutput(
      self,
      "vpcOutput",
      value=_vpc.vpc_id,
      description="VPC ID",
      export_name="vpcId"
    )

  @property
  def getVpc(self) -> _ec2.IVpc:
    return self._vpc
