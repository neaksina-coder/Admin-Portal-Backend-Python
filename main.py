from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db.base import Base
from db.session import engine
from api.v1.api_router import api_router
import time
from sqlalchemy.exc import OperationalError
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from utils.admin_digest import generate_and_store_daily_digest

MAX_RETRIES = 5
RETRY_DELAY = 5 # seconds
SCHEDULER_TZ = "Asia/Phnom_Penh"

_scheduler: BackgroundScheduler | None = None

def create_tables():
    for i in range(MAX_RETRIES):
        try:
            # Create tables if they don't exist; do not drop existing data.
            Base.metadata.create_all(bind=engine)
            print("Database tables created (if missing) successfully!")
            break
        except OperationalError:
            print(f"Database connection failed. Retrying in {RETRY_DELAY} seconds... ({i+1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
    else:
        raise Exception("Could not connect to the database after multiple retries.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    create_tables()
    _start_scheduler()
    yield
    # Shutdown: Clean up resources if needed
    _stop_scheduler()


def _start_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        return
    scheduler = BackgroundScheduler(timezone=ZoneInfo(SCHEDULER_TZ))
    scheduler.add_job(
        generate_and_store_daily_digest,
        CronTrigger(hour=6, minute=0),
        id="admin_digest_daily",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler


def _stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None

def include_router(app):
    app.include_router(api_router, prefix="/api/v1")

def start_application():
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    os.makedirs("uploads/profile_images", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    include_router(app)
    return app

app = start_application()

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    # Run the server on localhost:8000 with auto-reload enabled
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
