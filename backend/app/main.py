from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.routers import (
    appointment,
    auth,
    common,
    donor,
    evaluation,
    external,
    feedback,
    group,
    health,
    stats,
)
from app.seed import ensure_admin, seed_groups, seed_locations


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_admin(db)
        seed_locations(db)
        seed_groups(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = settings.api_prefix
app.include_router(common.router, prefix=api)
app.include_router(auth.router, prefix=api)
app.include_router(donor.router, prefix=api)
app.include_router(appointment.router, prefix=api)
app.include_router(health.router, prefix=api)
app.include_router(group.router, prefix=api)
app.include_router(feedback.router, prefix=api)
app.include_router(evaluation.router, prefix=api)
app.include_router(stats.router, prefix=api)
app.include_router(external.router, prefix=api)


@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs", "api_prefix": api}
