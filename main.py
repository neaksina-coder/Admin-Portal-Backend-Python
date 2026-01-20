from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.base import Base
from db.session import engine
from api.v1.api_router import api_router
import time
from sqlalchemy.exc import OperationalError

MAX_RETRIES = 5
RETRY_DELAY = 5 # seconds

def create_tables():
    for i in range(MAX_RETRIES):
        try:
            # Drop all tables first (for development purposes)
            Base.metadata.drop_all(bind=engine)
            # Create all tables
            Base.metadata.create_all(bind=engine)
            print("Database tables dropped and created successfully!")
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
    yield
    # Shutdown: Clean up resources if needed
    pass

def include_router(app):
    app.include_router(api_router, prefix="/api/v1")

def start_application():
    app = FastAPI(lifespan=lifespan)
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
