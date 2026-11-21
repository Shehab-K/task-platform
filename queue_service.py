import json
import os
import boto3

SQS_ENDPOINT_URL = os.getenv("SQS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
QUEUE_NAME = os.getenv("QUEUE_NAME", "task-queue")
DLQ_NAME = os.getenv("DLQ_NAME", "task-dlq")
MAX_RECEIVE_COUNT = os.getenv("MAX_RECEIVE_COUNT", "3")
VISIBILITY_TIMEOUT = os.getenv("VISIBILITY_TIMEOUT", "10")

sqs_client = boto3.client(
    "sqs",
    endpoint_url=SQS_ENDPOINT_URL,
    region_name=AWS_REGION,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)


def get_or_create_dlq_arn() -> str:
    dlq_response = sqs_client.create_queue(QueueName=DLQ_NAME)
    dlq_url = dlq_response["QueueUrl"]

    attrs = sqs_client.get_queue_attributes(
        QueueUrl=dlq_url,
        AttributeNames=["QueueArn"],
    )
    return attrs["Attributes"]["QueueArn"]


def get_or_create_queue_url() -> str:
    dlq_arn = get_or_create_dlq_arn()
    response = sqs_client.create_queue(QueueName=QUEUE_NAME)
    queue_url = response["QueueUrl"]

    redrive_policy = json.dumps(
        {
            "deadLetterTargetArn": dlq_arn,
            "maxReceiveCount": str(MAX_RECEIVE_COUNT),
        }
    )

    sqs_client.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={
            "RedrivePolicy": redrive_policy,
            "VisibilityTimeout": str(VISIBILITY_TIMEOUT),
        },
    )
    return queue_url


def send_task_to_queue(task_id: int) -> None:
    queue_url = get_or_create_queue_url()

    message_body = json.dumps({"task_id": task_id})

    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
    )