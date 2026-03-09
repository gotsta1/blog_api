from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine, Base
from app.redis import redis_client
from app.routers.posts import router as posts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await redis_client.aclose()
    await engine.dispose()


app = FastAPI(title="Blog API", lifespan=lifespan)
app.include_router(posts_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
