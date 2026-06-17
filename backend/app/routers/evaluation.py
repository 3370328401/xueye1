from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_staff, get_current_user
from app.models import Appointment, Evaluation, User
from app.schemas import AdminEvaluationOut, EvaluationIn, EvaluationOut

router = APIRouter(prefix="/evaluations", tags=["献血评价"])


@router.post("", response_model=EvaluationOut)
def submit_evaluation(
    data: EvaluationIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appt = db.get(Appointment, data.appointment_id)
    if not appt or appt.user_id != user.id:
        raise HTTPException(status_code=404, detail="预约不存在")
    ev = Evaluation(
        user_id=user.id,
        appointment_id=data.appointment_id,
        env_score=data.env_score,
        attitude_score=data.attitude_score,
        wait_score=data.wait_score,
        skill_score=data.skill_score,
        notice_score=data.notice_score,
        overall_score=data.overall_score,
        suggestion=data.suggestion,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


@router.get("/mine", response_model=list[EvaluationOut])
def my_evaluations(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.query(Evaluation)
        .filter(Evaluation.user_id == user.id)
        .order_by(Evaluation.created_at.desc())
        .all()
    )


@router.get("/admin/list", response_model=list[AdminEvaluationOut])
def admin_list(_: User = Depends(get_current_staff), db: Session = Depends(get_db)):
    rows = db.query(Evaluation).order_by(Evaluation.created_at.desc()).all()
    result = []
    for ev in rows:
        item = AdminEvaluationOut.model_validate(ev)
        user = db.get(User, ev.user_id)
        appt = db.get(Appointment, ev.appointment_id)
        item.user_name = user.name if user else ""
        item.user_phone = user.phone if user else ""
        item.appointment_code = appt.code if appt else ""
        result.append(item)
    return result
