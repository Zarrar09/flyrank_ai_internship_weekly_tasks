from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

#To add tasks: curl.exe -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\": \"Buy milk\"}"

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
async def addTask(request: Request):
    body = await request.json()
    title = body.get("title")
    
    if not title:
        return JSONResponse(status_code=400, content={"error": "You did not provide a title"})
    
    maxID = 0
    for i in range(len(tasks)):
        if int(tasks[i]["id"]) > maxID:
            maxID = int(tasks[i]["id"])
    maxID = int(tasks[lastIndex]["id"]) + 1
    tasks.append(
        {
            "id": maxID,
            "title": title,
            "done": False,
        }
    )
    return JSONResponse(status_code=201, content="Created, the polite way to say done.")