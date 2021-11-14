import json
from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_rds as _rds
from aws_cdk import aws_secretsmanager as _sm

class RDSStack(cdk.Stack):
  def __init__(self, scope: cdk.Construct, construct_id: str, vpc: _ec2.IVpc, sg:_ec2.ISecurityGroup, buildConfigs,  **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # extracting build configs
    environment = buildConfigs["Environment"]
    isProd = True if environment == "prod" else False

    # configuring environment specific settings
  
    # ensure retaining file system on production environment
    removalPolicy = cdk.RemovalPolicy.RETAIN if isProd else cdk.RemovalPolicy.DESTROY
    instanceSize = _ec2.InstanceSize.LARGE if isProd else _ec2.InstanceSize.SMALL
    storageSize = 100 if isProd else 20
    
    # creating mysql credentials using Secrets Manager
    mysqlSecret = _sm.Secret(
      self,
      "MySQLCredentials",
      secret_name="mysql-credentials",
      generate_secret_string=_sm.SecretStringGenerator(
        secret_string_template=json.dumps({
          "username": "admin",
        }),
        exclude_punctuation=True,
        include_space=False,
        generate_string_key="password"
      ),
    )

    #create MySQL RDS
    rds_db = _rds.DatabaseInstance(
      self, 
      "MySQL_DB",
      engine=_rds.DatabaseInstanceEngine.mysql(
        version=_rds.MysqlEngineVersion.VER_5_7_30,
      ),
      instance_type=_ec2.InstanceType.of(
        _ec2.InstanceClass.BURSTABLE2, instanceSize
      ),
      vpc=vpc,
      vpc_subnets=_ec2.SubnetSelection(
        subnet_type=_ec2.SubnetType.ISOLATED,
      ),
      database_name="webshop",
      multi_az=isProd,
      security_groups=[sg],
      allocated_storage=storageSize,
      storage_type=_rds.StorageType.GP2,
      credentials=_rds.Credentials.from_secret(
        secret=mysqlSecret,
      ),
      cloudwatch_logs_exports=[
        "audit", "error", "general", "slowquery"
      ],
      removal_policy=removalPolicy,
      deletion_protection=isProd,
      delete_automated_backups=isProd,
      backup_retention=cdk.Duration.days(7),
      parameter_group=_rds.ParameterGroup.from_parameter_group_name(
        self, "para-group-mysql",
        parameter_group_name="default.mysql5.7"
      )
    )
    
    # assigning our resource to be able to reference it
    # across stacks
    self._rds_db = rds_db
    self._mysqlSecret = mysqlSecret

    # output RDS resource
    cdk.CfnOutput(
      self,
      "rdsOutput",
      value=rds_db.db_instance_endpoint_address,
      export_name="rdsEndpointAddress"
    )

    # output resource
    cdk.CfnOutput(
      self,
      "mysqlSecretName",
      value=mysqlSecret.secret_name,
      export_name="mysqlSecretName"
    )
    cdk.CfnOutput(
      self,
      "mysqlSecretArn",
      value=mysqlSecret.secret_arn,
      export_name="mysqlSecretArn"
    )
    cdk.CfnOutput(
      self,
      "mysqlSecretFullArn",
      value=mysqlSecret.secret_full_arn,
      export_name="mysqlSecretFullArn"
    )

  @property
  def getRds(self) -> _rds.IDatabaseInstance:
    return self._rds_db
  @property
  def getMySqlSecret(self) -> _sm.ISecret:
    return self._mysqlSecret
