from fastapi import FastAPI
from supabase_client import supabase

app = FastAPI()

@app.on_event("startup")
async def startup():
    print("Server is running and connected to supabase")
    
@app.get("/")
async def root():
    return {"status": "ok"}