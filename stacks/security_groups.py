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

    # Creating the SG for our web server EC2 instances
    _webserver_ec2_sg = _ec2.SecurityGroup(
      self,
      "webserverEc2SG",
      allow_all_outbound=True,
      vpc=vpc,
      description="Security group for web server EC2 instances"
    )

    # Creating the SG for our internet-facing 
    # application load balancer
    _webserver_alb_sg = _ec2.SecurityGroup(
      self,
      "webserverAlbSG",
      allow_all_outbound=True,
      vpc=vpc,
      description="Security group for web servers ALB"
    )

    # adding ingress/egress rules for our RDS SG

    # allow MySQL client access to port 3306 from bastion EC2 SG
    _rds_sg.add_ingress_rule(
      peer=_bastion_ec2_sg,
      connection=_ec2.Port.tcp(3306),
      description="allow MySQL client access from bastion EC2 SG"
    )
    # allow MySQL client access to port 3306 from webservers SG
    _rds_sg.add_ingress_rule(
      peer=_webserver_ec2_sg,
      connection=_ec2.Port.tcp(3306),
      description="allow MySQL client access from web server EC2 SG"
    )
    
    # adding ingress/egress rules for our web server instances SG

    # allow SSH client access to port 22 from bastion EC2 SG
    _webserver_ec2_sg.add_ingress_rule(
      peer=_bastion_ec2_sg,
      connection=_ec2.Port.tcp(22),
      description="allow SSH client access from bastion EC2 SG"
    )
    # allow HTTP traffic to port 80 from webserver ALB SG
    _webserver_ec2_sg.add_ingress_rule(
      peer=_webserver_alb_sg,
      connection=_ec2.Port.tcp(80),
      description="allow HTTP from webserver ALB SG"
    )
    
    # adding ingress/egress rules for our web server ALB SG

    # allow HTTP traffic to port 80 from internet
    _webserver_alb_sg.add_ingress_rule(
      peer=_ec2.Peer.any_ipv4(),
      connection=_ec2.Port.tcp(80),
      description="allow HTTP traffic to port 80 from internet"
    )
    # allow HTTPS traffic to port 443 from internet
    _webserver_alb_sg.add_ingress_rule(
      peer=_ec2.Peer.any_ipv4(),
      connection=_ec2.Port.tcp(443),
      description="allow HTTPS traffic to port 80 from internet"
    )

    # assigning our SG resource to be able to reference it
    # across stacks
    self._bastion_ec2_sg = _bastion_ec2_sg
    self._rds_sg = _rds_sg
    self._webserver_ec2_sg = _webserver_ec2_sg
    self._webserver_alb_sg = _webserver_alb_sg

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
    cdk.CfnOutput(
      self,
      "webserverEc2SGOutput",
      value=_webserver_ec2_sg.security_group_id,
      export_name="webserverEc2SGId"
    )
    cdk.CfnOutput(
      self,
      "webserverAlbSGOutput",
      value=_webserver_alb_sg.security_group_id,
      export_name="webserverAlbSGId"
    )

  @property
  def getRdsSg(self) -> _ec2.ISecurityGroup:
    return self._rds_sg
  @property
  def getBastionEc2Sg(self) -> _ec2.ISecurityGroup:
    return self._bastion_ec2_sg
  @property
  def getWebserverEc2Sg(self) -> _ec2.ISecurityGroup:
    return self._webserver_ec2_sg
  @property
  def getWebserverAlbSg(self) -> _ec2.ISecurityGroup:
    return self._webserver_alb_sg
