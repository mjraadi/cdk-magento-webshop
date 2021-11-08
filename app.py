#!/usr/bin/env python3
import os
from aws_cdk import core as cdk

from stacks.vpc import VpcStack


app = cdk.App()
VpcStack(app, "VpcStack")

app.synth()
