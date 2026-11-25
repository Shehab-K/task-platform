import json

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db
from queue_service import DLQ_NAME, send_task_to_queue, sqs_client

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cloud-Native Task Platform")


@app.get("/")
def mainpage():
    return {"message": "welcome to the task manager"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED
)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(title=task.title, description=task.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    send_task_to_queue(db_task.id)
    return db_task


@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()


@app.get("/tasks/dlq")
def get_dlq_messages():
    dlq_url = sqs_client.create_queue(QueueName=DLQ_NAME)["QueueUrl"]

    attrs = sqs_client.get_queue_attributes(
        QueueUrl=dlq_url,
        AttributeNames=["ApproximateNumberOfMessages"],
    )
    message_count = int(attrs["Attributes"].get("ApproximateNumberOfMessages", 0))
    response = sqs_client.receive_message(
        QueueUrl=dlq_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=1,
        VisibilityTimeout=0,
    )
    messages = [
        {
            "message_id": msg["MessageId"],
            "body": json.loads(msg["Body"]),
        }
        for msg in response.get("Messages", [])
    ]

    return {
        "queue": DLQ_NAME,
        "approximate_message_count": message_count,
        "messages": messages,
    }


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="task not found"
        )
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    db.delete(task)
    db.commit()
    return None