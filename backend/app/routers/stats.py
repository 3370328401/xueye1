from collections import Counter
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models import (
    Appointment,
    Evaluation,
    Feedback,
    GroupApplication,
    User,
)

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/cards")
def stat_cards(_: User = Depends(get_current_staff), db: Session = Depends(get_db)):
    total_users = db.query(User).filter(User.role == "user").count()
    total_appointments = db.query(Appointment).count()
    today_str = date.today().isoformat()
    today_appointments = (
        db.query(Appointment).filter(Appointment.appoint_date == today_str).count()
    )
    completed = (
        db.query(Appointment)
        .filter(Appointment.status == "已完成现场采血")
        .count()
    )
    group_count = db.query(GroupApplication).count()
    pending_feedback = (
        db.query(Feedback).filter(Feedback.status != "已解决").count()
    )
    avg_score = db.query(func.avg(Evaluation.overall_score)).scalar()
    return {
        "total_users": total_users,
        "total_appointments": total_appointments,
        "today_appointments": today_appointments,
        "completed_appointments": completed,
        "group_applications": group_count,
        "pending_feedbacks": pending_feedback,
        "avg_evaluation_score": round(avg_score, 2) if avg_score else 0,
    }


@router.get("/appointment-status")
def appointment_status(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    rows = db.query(Appointment.status).all()
    counter = Counter(r[0] for r in rows)
    return [{"name": k, "value": v} for k, v in counter.items()]


@router.get("/daily-trend")
def daily_trend(_: User = Depends(get_current_staff), db: Session = Depends(get_db)):
    rows = db.query(Appointment.appoint_date).all()
    counter = Counter(r[0] for r in rows)
    items = sorted(counter.items())
    return {
        "dates": [k for k, _ in items],
        "counts": [v for _, v in items],
    }


@router.get("/blood-type")
def blood_type_stats(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    rows = db.query(Appointment.blood_type).all()
    counter = Counter(r[0] for r in rows)
    return [{"name": k, "value": v} for k, v in counter.items()]


@router.get("/feedback-status")
def feedback_status(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    rows = db.query(Feedback.status).all()
    counter = Counter(r[0] for r in rows)
    return [{"name": k, "value": v} for k, v in counter.items()]
