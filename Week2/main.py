from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

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