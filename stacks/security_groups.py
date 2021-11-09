from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as _ec2

class SecurityGroupsStack(cdk.Stack):
  def __init__(self, scope: cdk.Construct, construct_id: str, vpc: _ec2.IVpc, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # Creating the SG for our EFS resource
    _efs_sg = _ec2.SecurityGroup(
      self,
      "efsSG",
      allow_all_outbound=True,
      vpc=vpc,
      description="Security group for EFS"
    )
    
    # Creating the SG for our Bastion EC2 instances
    _bastion_ec2_sg = _ec2.SecurityGroup(
      self,
      "bastionEc2SG",
      allow_all_outbound=True,
      vpc=vpc,
      description="Security group for Bastion EC2 instances"
    )

    # adding ingress/egress rules for our bastion EC2 SG

    # allow ssh from anywhere
    _bastion_ec2_sg.add_ingress_rule(
      # TODO: read from environment context and limit the access
      peer=_ec2.Peer.any_ipv4(),
      connection=_ec2.Port.tcp(22),
      description="Allow SSH access from anywhere"
    )

    # adding ingress/egress rules for our EFS SG

    # allow NFS access to port 2049 from bastion EC2 SG
    _efs_sg.add_ingress_rule(
      peer=_bastion_ec2_sg,
      connection=_ec2.Port.tcp(2049),
      description="allow NFS access from bastion EC2 SG"
    )

    # assigning our SG resource to be able to reference it
    # across stacks
    self._bastion_ec2_sg = _bastion_ec2_sg
    self._efs_sg = _efs_sg

    # output SG resources
    cdk.CfnOutput(
      self,
      "efsSGOutput",
      value=_efs_sg.security_group_id,
      export_name="efsSGId"
    )
    cdk.CfnOutput(
      self,
      "bastionEc2SGOutput",
      value=_bastion_ec2_sg.security_group_id,
      export_name="bastionEc2SGId"
    )

  @property
  def getEfsSg(self) -> _ec2.ISecurityGroup:
    return self._efs_sg
  @property
  def getBastionEc2Sg(self) -> _ec2.ISecurityGroup:
    return self._bastion_ec2_sg
