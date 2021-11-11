# This function is triggered by an S3 PutObject event notification.
# It reads the file from the bucket and uses Amazon Rekognition
# DetectModerationLabels API to moderate the content. If a content
# is inappropriate, the object is tag with 
# "inappropriateContent: true" tag
import boto3
import json
import logging
import os

_s3_client = boto3.client('s3')
_rekognition_client = boto3.client("rekognition")

def readObject(bucketName, objectKey):
  # reading file from s3 bucket and passing it as bytes
  try:
    fileObj = _s3_client.get_object(
      Bucket=bucketName,
      Key=objectKey,
    )
    file_content = fileObj["Body"].read()
    return file_content
  except Exception as e:
    LOGGER.error(f"{str(e)}")
    raise

def detectLabels(objectFile):
  res = _rekognition_client.detect_moderation_labels(
    Image={
      "Bytes": objectFile
    },
    MinConfidence=90
  )
  labels = []
  LOGGER.info(f"received_label:{res}")
  try:
    if "ModerationLabels" in res:
      for label in res["ModerationLabels"]:
        lbl = {
          "name": label["Name"],
          "confidence": label["Confidence"]
        }
        LOGGER.info(f"received_label:{lbl}")
        labels.append(lbl)

  except Exception as e:
    LOGGER.error(f"{str(e)}")
    raise
  # TODO: set a "inappropriateContent" boolean tag to the object
  return labels

def lambda_handler(event, context):
  global LOGGER
  LOGGER = logging.getLogger()
  LOGGER.setLevel(level=os.getenv("LOG_LEVEL", "INFO").upper())

  LOGGER.info(f"received_event:{event}")

  try:
    if "Records" in event:
      bucket = event["Records"][0]["s3"]["bucket"]
      object = event["Records"][0]["s3"]["object"]

      bucketName = bucket["name"]
      objectKey = object["key"]

      file = readObject(bucketName, objectKey)
      lables = detectLabels(file)
      response = {
        "statusCode": 200,
        "body": json.dumps({"message": {
          "labels": lables
        }})
      }
      return response

  except Exception as e:
    LOGGER.error(f"{str(e)}")
    return {
      "statusCode": 400,
      "body": json.dumps({
        "message": f"ERROR:{str(e)}"
      })
    }

  response = {
    "statusCode": 400,
    "body": json.dumps({"message": "something went wrong"})
  }

  return response
