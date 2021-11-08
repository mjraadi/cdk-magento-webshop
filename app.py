#!/usr/bin/env python3

# importing libraries
import os
from aws_cdk import core as cdk
# importing stack constructs
from stacks.vpc import VpcStack
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
VpcStack(app, stackName, env=_env, buildConfigs=buildConfigs)

app.synth()
