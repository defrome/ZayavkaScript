import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.db import create_tables
from routes import master_router, application_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, create_tables)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(master_router.router)
app.include_router(application_router.router)
