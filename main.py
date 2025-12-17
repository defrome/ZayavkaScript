import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, Form
from sqlalchemy.orm import Session
from database.db import create_tables, get_db
from models.masters import Master
from routes import master_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, create_tables)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(master_router.router)
