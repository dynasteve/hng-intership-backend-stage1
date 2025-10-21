from contextlib import asynccontextmanager
from unittest.mock import Base
from fastapi import FastAPI
from .routes import strings
from .database import engine
from . import models

# Ensure tables are created (for dev/demo). In prod use migrations (alembic).
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown code (optional)
    # e.g., closing resources

app = FastAPI(title="HNG Internship Backend Stage 1", lifespan=lifespan)

app.include_router(strings.router)

@app.get("/")
def root():
    return {"message": "Welcome to String Analyzer Service!"}
