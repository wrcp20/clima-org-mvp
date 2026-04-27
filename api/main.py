from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables
from routers.admin import router as admin_router
from routers.surveys import router as surveys_router
from routers.scores import router as scores_router
from routers.responses import router as responses_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Clima Organizacional MVP",
    version="0.1.0",
    description="API para análisis de clima organizacional y detección de burnout",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://dashboard:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(surveys_router, tags=["surveys"])
app.include_router(scores_router, prefix="/admin", tags=["scores"])
app.include_router(responses_router, prefix="/admin", tags=["responses"])


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "version": "0.1.0"}
