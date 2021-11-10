from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as _ec2

class SecurityGroupsStack(cdk.Stack):
  def __init__(self, scope: cdk.Construct, construct_id: str, vpc: _ec2.IVpc, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # Creating the SG for our RDS resource
    _rds_sg = _ec2.SecurityGroup(
      self,
      "rdsSG",
      allow_all_outbound=True,
      vpc=vpc,
      description="Security group for RDS"
    )
    
    # Creating the SG for our Bastion EC2 instances
    _bastion_ec2_sg = _ec2.SecurityGroup(
      self,
      "bastionEc2SG",
      allow_all_outbound=True,
      vpc=vpc,
      description="Security group for Bastion EC2 instances"
    )

    # adding ingress/egress rules for our RDS SG

    # allow MySQL client access to port 3306 from bastion EC2 SG
    _rds_sg.add_ingress_rule(
      peer=_bastion_ec2_sg,
      connection=_ec2.Port.tcp(3306),
      description="allow MySQL client access from bastion EC2 SG"
    )

    # assigning our SG resource to be able to reference it
    # across stacks
    self._bastion_ec2_sg = _bastion_ec2_sg
    self._rds_sg = _rds_sg

    # output SG resources
    cdk.CfnOutput(
      self,
      "rdsSGOutput",
      value=_rds_sg.security_group_id,
      export_name="rdsSGId"
    )
    cdk.CfnOutput(
      self,
      "bastionEc2SGOutput",
      value=_bastion_ec2_sg.security_group_id,
      export_name="bastionEc2SGId"
    )

  @property
  def getRdsSg(self) -> _ec2.ISecurityGroup:
    return self._rds_sg
  @property
  def getBastionEc2Sg(self) -> _ec2.ISecurityGroup:
    return self._bastion_ec2_sg
