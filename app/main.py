from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import strings
from app.database import Base, engine
import app.models  # import all models so Base.metadata is populated

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code: create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown code (optional)

app = FastAPI(title="String Analyzer Service", lifespan=lifespan)
app.include_router(strings.router)

@app.get("/")
def root():
    return {"message": "Welcome to String Analyzer Service!"}
