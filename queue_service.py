import json
import boto3

SQS_ENDPOINT_URL = "http://localhost:4566"
AWS_REGION = "eu-central-1"
QUEUE_NAME = "task-queue"

sqs_client = boto3.client(
    "sqs",
    endpoint_url=SQS_ENDPOINT_URL,
    region_name=AWS_REGION,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

def get_or_create_queue_url() -> str:
    response = sqs_client.create_queue(QueueName=QUEUE_NAME)
    return response["QueueUrl"]

def send_task_to_queue(task_id:int)->None:
    queue_url=get_or_create_queue_url()

    message_body=json.dumps({"task_id":task_id})

    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
    )
