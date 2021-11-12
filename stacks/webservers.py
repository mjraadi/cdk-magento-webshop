import os.path
from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_secretsmanager as _sm
from aws_cdk import aws_autoscaling as _asg
from aws_cdk import aws_cloudfront as _cloudfront
from aws_cdk import aws_cloudfront_origins as _cf_origins
from aws_cdk import aws_elasticloadbalancingv2 as _elbv2

currentDirName = os.path.dirname(__file__)

# web server EC2 Instance configs
ec2_type = "t2.micro"
linux_ami = _ec2.AmazonLinuxImage(
  generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
  edition=_ec2.AmazonLinuxEdition.STANDARD,
  virtualization=_ec2.AmazonLinuxVirt.HVM,
  storage=_ec2.AmazonLinuxStorage.GENERAL_PURPOSE
)

class WebServersStack(cdk.Stack):
  def __init__(
    self, 
    scope: cdk.Construct, 
    construct_id: str,
    vpc: _ec2.IVpc,
    webserverEc2SG:_ec2.ISecurityGroup,
    webserverAlbSG: _ec2.ISecurityGroup,
    mappings,
    mysqlSecret: _sm.ISecret,
    buildConfigs,
    **kwargs,
  ) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # extracting build configs
    environment = buildConfigs["Environment"]
    isProd = True if environment == "prod" else False
    asgMinCapacity = 2 if isProd else 1
    asgMaxCapacity = 4 if isProd else 2

    # Instance Role and SSM Managed Policy
    _role = _iam.Role(
      self, 
      "WebServeerInstanceSSM", 
      assumed_by=_iam.ServicePrincipal("ec2.amazonaws.com")
    )
    _role.add_managed_policy(
      _iam.ManagedPolicy.from_aws_managed_policy_name(
        "AmazonSSMManagedInstanceCore"
      )
    )
    
    # create policy statement to be able to read mysql secret
    webserverGetSecretValuePolicyStatement = _iam.PolicyStatement(
      actions=[
        "secretsmanager:GetSecretValue"
      ],
      effect=_iam.Effect.ALLOW,
      resources=[mysqlSecret.secret_full_arn],
    )
    
    webserverGetSecretValuePolicy = _iam.Policy(
      self,
      "webserverPolicy",
      statements=[
        webserverGetSecretValuePolicyStatement
      ]
    )
    
    _role.attach_inline_policy(
      policy=webserverGetSecretValuePolicy,
    )

    with open("user_data/configure_webserver_instance.sh", 'r') as user_data_h:
      # Use a substitution
      user_data_sub = cdk.Fn.sub(user_data_h.read(), mappings)

    # Import substitution object into user_data set
    _user_data = _ec2.UserData.custom(user_data_sub)

    webserverALB = _elbv2.ApplicationLoadBalancer(
      self,
      "webserverALB",
      vpc=vpc,
      internet_facing=True,
      security_group=webserverAlbSG,
    )
    
    webserverAlbListener = webserverALB.add_listener(
      "webserverAlbHttpListener",
      port=80,
      open=True,
    )

    # Create web server instances auto scaling group
    webserverASG = _asg.AutoScalingGroup(
      self, 
      "webserverASG",
      vpc=vpc,
      instance_type=_ec2.InstanceType(
        instance_type_identifier=ec2_type
      ),
      role=_role,
      machine_image=linux_ami,
      min_capacity=asgMinCapacity,
      max_capacity=asgMaxCapacity,
      security_group=webserverEc2SG,
      user_data=_user_data,
      vpc_subnets=_ec2.SubnetSelection(
        subnet_type=_ec2.SubnetType.PRIVATE,
      ),
    )

    webserverAlbListener.add_targets(
      "webserverAlbHttpTargets",
      port=80,
      targets=[webserverASG],
      health_check=_elbv2.HealthCheck(
        path="/",
        unhealthy_threshold_count=2,
        healthy_threshold_count=5,
        interval=cdk.Duration.seconds(30),
      )
    )
    
    # add scaling policy for the Auto Scaling Group
    webserverASG.scale_on_request_count(
      "requests-per-minute",
      target_requests_per_minute=60
    )

    webserverASG.scale_on_cpu_utilization(
      "cpu-util-scaling",
      target_utilization_percent=75
    )
    
    webserversCfDistribution = _cloudfront.Distribution(
      self, 
      "webserversCfDistribution",
      default_behavior={
        "origin": _cf_origins.LoadBalancerV2Origin(
          webserverALB,
          protocol_policy=_cloudfront.OriginProtocolPolicy.HTTP_ONLY,
        )
      }
    )

    # assigning our resource to be able to reference it
    # across stacks
    self._webserverALB = webserverALB
    self._webserverASG = webserverASG
    self._webserversCfDistribution = webserversCfDistribution
    self._webserverRole = _role

    # output resource
    cdk.CfnOutput(
      self,
      "webserverALBOutput",
      value=webserverALB.load_balancer_dns_name,
      export_name="webserverAlbDnsName"
    )

  @property
  def getWebserverAlb(self) -> _elbv2.IApplicationLoadBalancer:
    return self._webserverALB
  @property
  def getWebserverAsg(self) -> _asg.IAutoScalingGroup:
    return self._webserverASG
  @property
  def getWebserverRole(self) -> _iam.IRole:
    return self._webserverRole
  @property
  def getWebserverCfDistribution(self) -> _cloudfront.IDistribution:
    return self._webserversCfDistribution
