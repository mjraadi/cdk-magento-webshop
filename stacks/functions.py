import os.path
from aws_cdk import core as cdk
from aws_cdk import aws_s3 as _s3
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_logs as _logs
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3_notifications as _s3_notifications

currentDirName = os.path.dirname(__file__)

class FunctionsStack(cdk.Stack):
  def __init__(self, scope: cdk.Construct, construct_id: str, vpc: _ec2.IVpc,buildConfigs,  **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # extracting build configs
    environment = buildConfigs["Environment"]
    isProd = True if environment == "prod" else False

    # configuring environment specific settings
  
    # ensure retaining file system on production environment
    removalPolicy = cdk.RemovalPolicy.RETAIN if isProd else cdk.RemovalPolicy.DESTROY

    # read lambda function code
    try:
      with open("functions/src/content_moderator.py", mode="r") as file:
        lambda_src = file.read()
    except OSError:
      print("Unable to read Lambda Function Code")

    # configure proper permissions
    # create policy statement
    rekognitionDetectModerationLabelsPolicySatement = _iam.PolicyStatement(
      actions=[
        "rekognition:DetectModerationLabels"
      ],
      effect=_iam.Effect.ALLOW,
      resources=["*"]
    )

    rekognitionPolicy = _iam.Policy(
      self,
      "rekognitionPolicy",
      statements=[
        rekognitionDetectModerationLabelsPolicySatement
      ]
    )

    # create the lambda function
    contentModeratorFn = _lambda.Function(
      self,
      "contentModeratorFn",
      function_name="contentModeratorFn",
      description="This function is called by S3 events and uses Amazon Rekognition API to check for inappropriate content",
      runtime=_lambda.Runtime.PYTHON_3_7,
      handler="index.lambda_handler",
      code=_lambda.InlineCode(
        lambda_src
      ),
      vpc=vpc,
      timeout=cdk.Duration.seconds(10),
      environment={
        "LOG_LEVEL": "INFO"
      }
    )
    
    # add rekognition detect labels policy statement
    contentModeratorFn.role.attach_inline_policy(
      policy=rekognitionPolicy
    )

    # create lambda function log group
    _logs.LogGroup(
      self,
      "myFunctionLogGroup",
      log_group_name=f"/aws/lambda/{contentModeratorFn.function_name}",
      removal_policy=cdk.RemovalPolicy.DESTROY,
      retention=_logs.RetentionDays.ONE_WEEK
    )
    
    # create the s3 bucket
    webShopContentBucket = _s3.Bucket(
      self,
      "webShopContentBucket",
      versioned=True,
      encryption=_s3.BucketEncryption.S3_MANAGED,
      public_read_access=True,
      removal_policy=removalPolicy,
    )
    
    webShopContentBucket.grant_read(
      contentModeratorFn.role,
    )
    
    # allowing the function to put tags on this S3 bucket objects
    webShopContentBucket.add_to_resource_policy(
      permission=_iam.PolicyStatement(
        actions=[
          "S3:PutObjectTagging"
        ],
        effect=_iam.Effect.ALLOW,
        resources=[
          webShopContentBucket.arn_for_objects("*"),
          webShopContentBucket.bucket_arn,
        ],
        principals=[
          _iam.ArnPrincipal(contentModeratorFn.role.role_arn)
        ]
      )
    )

    # create S3 bucket notification
    s3NotificationHandler = _s3_notifications.LambdaDestination(
      contentModeratorFn
    )

    webShopContentBucket.add_event_notification(
      _s3.EventType.OBJECT_CREATED, s3NotificationHandler
    )

    # assigning our resource to be able to reference it
    # across stacks
    self._contentModeratorFn = contentModeratorFn
    self._webShopContentBucket = webShopContentBucket
    
    # output resource
    cdk.CfnOutput(
      self,
      "webShopContentBucketNameOutput",
      value=webShopContentBucket.bucket_name,
      export_name="webShopContentBucketName"
    )

  @property
  def getContentModeratorFn(self) -> _lambda.IFunction:
    return self._contentModeratorFn
  @property
  def getWebShopContentBucket(self) -> _s3.IBucket:
    return self._webShopContentBucket
