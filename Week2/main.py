from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get('/')
async def root():
    return {"name": "TaskAPI", "version": "1.0", "endpoints": ["/tasks"]}

@app.get('/health', status_code = 200)
def getHealth():
    return {"status": "ok"}