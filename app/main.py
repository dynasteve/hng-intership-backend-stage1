from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from app.routes import strings
from app.database import Base, engine
from app.routes import strings
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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)