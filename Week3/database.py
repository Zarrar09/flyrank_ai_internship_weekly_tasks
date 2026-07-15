from contextlib import asynccontextmanager
import asyncpg
import os
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    yield
    await app.state.db_pool.close()