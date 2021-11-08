from aws_cdk import core as cdk


def getBuildConfigs(app: cdk.App):
    env = app.node.try_get_context("config")

    if env is None:
        raise Exception(
            "Context variable missing on CDK command. Pass in as `-c config=XXX`"
        )

    buildConfigs = app.node.try_get_context(env)
    return buildConfigs
