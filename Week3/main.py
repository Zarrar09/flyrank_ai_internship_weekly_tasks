from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import lifespan
import repository


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
async def allTasks(request: Request):
    pool = request.app.state.db_pool
    return await repository.get_all_tasks(pool)
    
@app.get("/tasks/{id}")
async def getTask(id : int, request: Request):
    pool = request.app.state.db_pool
    result = await repository.get_task(id=id, pool=pool)
    if result == None:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    else:
        return JSONResponse(status_code=200, content=result)
    
@app.post("/tasks")
async def addTask(task: TaskCreate, request: Request):
    title = task.title
    
    if not title:
        return JSONResponse(status_code=400, content={"error": "You did not provide a title"})
    
    pool = request.app.state.db_pool
    result = await repository.insert_task(title=title, pool=pool)
    
    return JSONResponse(status_code=201, content=result)

@app.put("/tasks/{id}")
async def replaceTask(id: int, task: TaskUpdate, request: Request):
    title = task.title
    done = task.done
    
    if title is None and done is None:
        return JSONResponse(status_code=400, content={"error": "You did not provide a title or done"})
    
    pool = request.app.state.db_pool
    result = await repository.replace_task(id, title, done, pool)
    
    if result is None:
        return JSONResponse(status_code=404, content={"error": f"{id} does not exist"})
    
    return JSONResponse(status_code=200, content=result)

@app.delete("/tasks/{id}")
async def deleteTask(id: int, request: Request):
    pool = request.app.state.db_pool
    result = await repository.delete_task(id, pool)
    
    if result is None:
        return JSONResponse(status_code=404, content={"error": f"{id} does not exist"})
    
    return JSONResponse(status_code=204)