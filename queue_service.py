import json
import boto3

SQS_ENDPOINT_URL="http://localhost:4566"
QUEUE_NAME="task-queue"


sqs_client=boto3.client(
    "sqs",
    endpoint_url="eu-central-1",
    region_name="AWS_REGION",
    aws_access_key_id="test",
    aws_secret_access_keys="test",
)

def get_or_create_queue_url()->str:
    response=sqs_client.create_queue(QUEUE_NAME=QUEUE_NAME)
    return response["queue url"]

def send_task_to_queue(task_id:int)->None:
    queue_url=get_or_create_queue_url()

    message_body=json.dumps({"task_id":task_id})

    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
    )
