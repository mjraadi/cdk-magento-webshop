from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_efs as _efs

class EFSStack(cdk.Stack):
  def __init__(self, scope: cdk.Construct, construct_id: str, vpc: _ec2.IVpc, sg:_ec2.ISecurityGroup, buildConfigs, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # extracting build configs
    environment = buildConfigs["Environment"]
    isProd = True if environment == "prod" else False

    # configuring environment specific settings
  
    # ensure retaining file system on production environment
    removalPolicy = cdk.RemovalPolicy.RETAIN if isProd else cdk.RemovalPolicy.DESTROY

    # Create a file system in EFS to store information
    _fs = _efs.FileSystem(
      self, 
      "FS",
      vpc=vpc,
      removal_policy=removalPolicy,
      security_group=sg,
      # files are not transitioned to infrequent access (IA) storage by default
      lifecycle_policy=_efs.LifecyclePolicy.AFTER_14_DAYS,
      performance_mode=_efs.PerformanceMode.GENERAL_PURPOSE,
      enable_automatic_backups=isProd,
      throughput_mode=_efs.ThroughputMode.BURSTING,
      vpc_subnets=_ec2.SubnetSelection(
        subnet_type=_ec2.SubnetType.ISOLATED,
      ),
    )

    # define file system access point
    _fsAP = _fs.add_access_point(
      "AccessPoint",
      create_acl=_efs.Acl(
        owner_gid="1001", owner_uid="1001", permissions="750"
      ),
      path="/data",
      posix_user=_efs.PosixUser(gid="1001", uid="1001")
    )

    # assigning our EFS resource to be able to reference it
    # across stacks
    self._efs = _fs
    self._efsAP = _fsAP

    # output EFS resource
    cdk.CfnOutput(
      self,
      "efsOutput",
      value=_fs.file_system_id,
      export_name="efsId"
    )
    cdk.CfnOutput(
      self,
      "efsAPOutput",
      value=_fsAP.access_point_id,
      export_name="efsApId"
    )

  @property
  def getEfs(self) -> _efs.IFileSystem:
    return self._efs
  @property
  def getEfsAp(self) -> _efs.IAccessPoint:
    return self._efsAP
