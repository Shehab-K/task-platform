from fastapi import Depends, FastAPI, HTTPException, status
from database import Base, engine, get_db
import models
import schemas
from sqlalchemy.orm import Session
from queue_service import send_task_to_queue

# Create database tables automatically on startup
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
    db.commit()  # Added missing ()
    db.refresh(db_task)


    send_task_to_queue(db_task.id)
    return db_task


@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()  # Fixed case to models.Task
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