from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
app=FastAPI()


tasks=[]


class TaskCreate(BaseModel):
    title:str
    description:str | None = None


class TaskUpdate(BaseModel):
    title:str | None=None
    description:str | None=None
    status:str | None=None


@app.get("/")
def mainpage():
    return {"message":"welcome to the task manager"}


@app.get("/health")
def health_check():
    return {"status":"healthy"}


@app.post("/tasks")
def create_task(task:TaskCreate):
    new_task={
        "id":len(tasks)+1,
        "title":task.title,
        "description":task.description,
        "status":"pending"
    }

    tasks.append(new_task)
    return new_task

@app.get("/tasks")
def get_tasks():
    return tasks



@app.get("/tasks/{task_id}")
def get_task(task_id:int):
    for task in tasks:
        if task["id"]==task_id:
            return task
    raise HTTPException(status_code=404,detail="Task not found")


#update an existing task
@app.put("/tasks/{task_id}")
def update_task(task_id:int,task_update:TaskUpdate):
    for task in tasks:
        if task["id"]==task_id:
            if task.title is not None:
                task["title"]=task_update.title
            if task.description is not None:
                task["description"]=task_update.description
            if task.status is not None:
                task["status"]=task_update.status
            return task
    raise HTTPException(status_code=404,detail="task is not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id:int):
    for i,task in enumerate(tasks):
        if task["id"]==task_id:
            tasks.pop(index)
            return {"detail":f"task {task_id} deleted"}
        raise HTTPException(status_code=404,detail="task not found")