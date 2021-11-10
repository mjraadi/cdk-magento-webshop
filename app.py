#!/usr/bin/env python3

# importing libraries
import os
from aws_cdk import core as cdk
# importing stack constructs
from stacks.vpc import VpcStack
from stacks.security_groups import SecurityGroupsStack
from stacks.rds import RDSStack
from stacks.bastion import BastionStack
from stacks.webservers import WebServersStack
# importing util functions
from utils import getBuildConfigs


# initiating a CDK app
app = cdk.App()

# reading project configs
buildConfigs = getBuildConfigs(app)

# setting global tags
globalTags = buildConfigs["GlobalTags"]
if globalTags is not None:
  for key in globalTags:
    cdk.Tags.of(app).add(key, globalTags[key])

# setting up the environment the stack is provisioned
_account = os.environ.get(
  "CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]
)
_region = os.environ.get(
  "CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]
)
_env = cdk.Environment(
  account=_account,
  region=_region
)

# main stack name
stackName = f"{buildConfigs['App']}-{buildConfigs['Environment']}"

# provisioning VPC stack
vpcStack = VpcStack(
  app, 
  stackName, 
  env=_env, 
  buildConfigs=buildConfigs
)

# provisioning security groups
securityGroupsStack = SecurityGroupsStack(
  app,
  f"{stackName}-sg",
  env=_env,
  vpc=vpcStack.getVpc
)

# provisioning our RDS stack
rdsStack = RDSStack(
  app,
  f"{stackName}-rds",
  env=_env,
  vpc=vpcStack.getVpc,
  sg=securityGroupsStack.getRdsSg,
  buildConfigs=buildConfigs,
)

userDataVarMappings = {
  "__AWS_ACCOUNT_ID__": _account,
  "__AWS_REGION__": _region,
  "__MYSQL_INSTANCE_ADDRESS__": rdsStack.getRds.db_instance_endpoint_address,
  "__MYSQL_SECRET_NAME__": rdsStack.getMySqlSecret.secret_name,
}

bastionStack = BastionStack(
  app,
  f"{stackName}-bastion-ec2",
  env=_env,
  vpc=vpcStack.getVpc,
  sg=securityGroupsStack.getBastionEc2Sg,
  mappings=userDataVarMappings,
  mysqlSecret=rdsStack.getMySqlSecret,
)

webServersStack = WebServersStack(
  app,
  f"{stackName}-webservers",
  env=_env,
  vpc=vpcStack.getVpc,
  webserverEc2SG=securityGroupsStack.getWebserverEc2Sg,
  webserverAlbSG=securityGroupsStack.getWebserverAlbSg,
  mappings=userDataVarMappings,
  mysqlSecret=rdsStack.getMySqlSecret,
  buildConfigs=buildConfigs,
)

app.synth()
