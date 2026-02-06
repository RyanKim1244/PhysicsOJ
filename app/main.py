"""OPC - Online Physics Competition Judge - Application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import init_db, SessionLocal
from app.routers import problems, submissions, competitions, stats
from app.services.seed_data import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB and seed data on startup."""
    init_db()
    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="OPC - Online Physics Competition Judge",
    description="물리학 대회 기출문제 온라인 저지 시스템",
    version="1.0.0",
    lifespan=lifespan,
)

# Routers
app.include_router(problems.router)
app.include_router(submissions.router)
app.include_router(competitions.router)
app.include_router(stats.router)

# Static files
app.mount("/static", StaticFiles(directory="app/templates/static"), name="static")


@app.get("/")
async def index():
    """Serve the main SPA page."""
    return FileResponse("app/templates/index.html")
