from aws_cdk import core as cdk
from aws_cdk.assertions import Template

from stacks.vpc import VpcStack


buildConfigs = {
  "App": "magento-webshop",
  "Environment": "dev",
  "GlobalTags": {
    "App": "magento-webshop-dev",
    "SupportEmail": "me@mjraadi.dev"
  },
  "Parameters": {
    "VPC": {
      "CIDR": "10.83.0.0/20",
      "CIDRMask": 24
    }
  }
}

def test_synthesizes_properly():
  app = cdk.App()

  vpcStack = VpcStack(
    app, 
    "test-vpc-stack", 
    buildConfigs=buildConfigs
  )
  template = Template.from_stack(vpcStack)
  
  template.has_resource_properties(
    "AWS::EC2::VPC",
    {
      "CidrBlock": "10.83.0.0/20"
    },
  )
