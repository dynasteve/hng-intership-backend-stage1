from fastapi import FastAPI
from .routes import strings
from .database import engine
from . import models

# Ensure tables are created (for dev/demo). In prod use migrations (alembic).
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HNG Internship Backend Stage 1")

app.include_router(strings.router)

@app.get("/")
def root():
    return {"message": "Welcome to String Analyzer Service!"}

@app.on_event("startup")
def init_db():
    from app.database import Base, engine
    import app.models
    Base.metadata.create_all(bind=engine)
    