import json
import time
from database import SessionLocal
import models
from queue_service import MAX_RECEIVE_COUNT, get_or_create_queue_url, sqs_client




def process_task(task_id: int) -> bool:
    db = SessionLocal()
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            print(f"[worker] Task {task_id} not found in database. Skipping.")
            return True

        if task.status == "completed":
            print(f"[worker] Task {task_id} already completed. Skipping duplicate message.")
            return True

        print(f"[worker] Processing task {task_id}: '{task.title}' (attempt {task.retry_count + 1})...")
        task.status = "processing"
        db.commit()

        time.sleep(3)

        
        if "fail" in task.title.lower():
            raise RuntimeError(f"Simulated processing error for task '{task.title}'")

        task.status = "completed"
        task.error_message = None
        db.commit()
        print(f"[worker] Finished task {task_id} -> status set to 'completed'.")
        return True

    except Exception as exc:
        db.rollback()
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if task:
            task.retry_count += 1
            task.error_message = str(exc)
            max_retries = int(MAX_RECEIVE_COUNT)
            task.status = "failed" if task.retry_count >= max_retries else "retrying"
            db.commit()
            print(
                f"[worker] Task {task_id} failed (attempt {task.retry_count}/{max_retries}): {exc}"
            )
        
        return False
    finally:
        db.close()



def run_worker() -> None:
    queue_url = get_or_create_queue_url()
    print(f"[worker] Listening for jobs on {queue_url}...")

    while True:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        messages = response.get("Messages", [])
        for message in messages:
            body = json.loads(message["Body"])
            task_id = body["task_id"]

            
            succeeded = process_task(task_id)
            if succeeded:
                sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message["ReceiptHandle"],
                )
            


if __name__ == "__main__":
    run_worker()