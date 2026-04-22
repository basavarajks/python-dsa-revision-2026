from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import ask, auth, dashboard, memories

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "MemoryVault AI backend is running"}


app.include_router(auth.router)
app.include_router(memories.router)
app.include_router(ask.router)
app.include_router(dashboard.router)
