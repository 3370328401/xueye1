from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.routers import (
    appointment,
    audit,
    auth,
    common,
    dict as dict_router,
    donor,
    double_form,
    evaluation,
    external,
    feedback,
    group,
    health,
    message,
    personal,
    points,
    poster,
    queue,
    reports,
    schedule,
    stats,
    system,
)
from app.seed import (
    ensure_admin,
    seed_demo_users,
    seed_dicts,
    seed_group_activities,
    seed_groups,
    seed_locations,
    seed_eval_templates,
    seed_gifts,
    seed_messages,
    seed_orgs,
    seed_poster_templates,
    seed_staff,
    seed_sys_params,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_admin(db)
        seed_staff(db)
        seed_dicts(db)
        seed_locations(db)
        seed_demo_users(db)
        seed_groups(db)
        seed_poster_templates(db)
        seed_group_activities(db)
        seed_eval_templates(db)
        seed_gifts(db)
        seed_messages(db)
        seed_orgs(db)
        seed_sys_params(db)
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
app.include_router(dict_router.router, prefix=api)
app.include_router(audit.router, prefix=api)
app.include_router(double_form.router, prefix=api)
app.include_router(poster.router, prefix=api)
app.include_router(schedule.router, prefix=api)
app.include_router(points.router, prefix=api)
app.include_router(queue.router, prefix=api)
app.include_router(message.router, prefix=api)
app.include_router(personal.router, prefix=api)
app.include_router(system.router, prefix=api)
app.include_router(reports.router, prefix=api)


@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs", "api_prefix": api}
