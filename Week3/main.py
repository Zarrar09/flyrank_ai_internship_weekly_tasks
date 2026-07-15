from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import lifespan


app = FastAPI(lifespan=lifespan)

# To add tasks: curl.exe -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\": \"Buy milk\"}"

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

tasks = [
    {
        "id": 99,
        "title": "FirstAPI",
        "done": False ,
    },
    {
        "id": 100,
        "title": "Complete GitHub Repo",
        "done": False, 
    },
    {
        "id": 101,
        "title": "Complete Assignment 2",
        "done": False, 
    },
]

@app.get('/')
async def root():
    return {"name": "TaskAPI", "version": "1.0", "endpoints": ["/tasks"]}

@app.get('/health', status_code = 200)
def getHealth():
    return {"status": "ok"}

@app.get('/tasks')
def allTasks():
    return tasks
    
@app.get("/tasks/{id}")
def getTask(id : int):
    for i in range(len(tasks)):
        if id == tasks[i]['id']:
            return JSONResponse(status_code=200, content=tasks[i])
    else:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    
@app.post("/tasks")
async def addTask(task: TaskCreate):
    title = task.title
    
    if not title:
        return JSONResponse(status_code=400, content={"error": "You did not provide a title"})
    
    maxID = 0
    for i in range(len(tasks)):
        if int(tasks[i]["id"]) > maxID:
            maxID = int(tasks[i]["id"])
    maxID += 1
    tasks.append(
        {
            "id": maxID,
            "title": title,
            "done": False,
        }
    )
    return JSONResponse(status_code=201, content=tasks[len(tasks) - 1])

@app.put("/tasks/{id}")
async def replaceTask(id : int, task: TaskUpdate):
    
    title = task.title
    done = task.done
    
    if title is None and done is None:
        return JSONResponse(status_code=400, content={"error": "You did not provide a title or done"})
    
    for i in range(len(tasks)):
        if id == tasks[i]["id"]:
            if title is not None:
                tasks[i]["title"] = title
            if done is not None:
                tasks[i]["done"] = done
            return JSONResponse(status_code=200, content=tasks[i])
            
    return JSONResponse(status_code=404, content={"error": f"{id} does not exist"})

@app.delete("/tasks/{id}")
async def deleteTask(id : int):
    for i in range(len(tasks)):
        if tasks[i]["id"] == id:
            tasks.pop(i)
            return JSONResponse(status_code=204, content=tasks[i])
        
    return JSONResponse(status_code=404, content={"error": f"{id} does not exist"})