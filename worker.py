import json 
import time
from database import SessionLocal
import models
from queue_service import get_or_create_queue_url,sqs_client


def process_task(task_id:int)->None:
    db=SessionLocal()
    try:
        task=db.query(models.Task).filter(models.Task.id==task_id).first()
        if not task:
            print(f"[worker]Task {task_id} not found in database.skipping.")
            return

        print(f"[worker] processing task {task_id}:'{task.title}'...")
        task.status="processing"
        db.commit()

        time.sleep(5)

        task.status="completed"
        db.commit()
        print(f"[worker] finished task {task_id}-> status set to 'completed' .") 
        print(f"[worker] finished task {task_id}-> status set to 'completed'")
    finally:
        db.close()


def run_worker()->None:
    queue_url=get_or_create_queue_url()
    print(f"[worker] listening for jobs on {queue_url}...")

    while True:
        response=sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        messages=response.get("Messages",[])
        for message in messages:
            body=json.loads(message["Body"])
            task_id=body["task_id"]

            process_task(task_id)

            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message["ReceiptHandle"],
            )


if __name__ =="__main__":
    run_worker()