from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_user
from app.models import Appointment, Feedback, User
from app.schemas import AdminFeedbackOut, FeedbackIn, FeedbackOut, FeedbackStatusIn

router = APIRouter(prefix="/feedbacks", tags=["异常反馈"])

FEEDBACK_STATUSES = ["已反馈", "正在联系处理", "已解决"]


@router.post("", response_model=FeedbackOut)
def submit_feedback(
    data: FeedbackIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appt = db.get(Appointment, data.appointment_id)
    if not appt or appt.user_id != user.id:
        raise HTTPException(status_code=404, detail="预约不存在")
    fb = Feedback(
        user_id=user.id,
        appointment_id=data.appointment_id,
        swelling=data.swelling,
        redness=data.redness,
        arm_pain=data.arm_pain,
        other_desc=data.other_desc,
        contact_phone=data.contact_phone,
        status="已反馈",
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


@router.get("/mine", response_model=list[FeedbackOut])
def my_feedbacks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Feedback)
        .filter(Feedback.user_id == user.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )


@router.get("/admin/list", response_model=list[AdminFeedbackOut])
def admin_list(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    result = []
    for fb in rows:
        item = AdminFeedbackOut.model_validate(fb)
        user = db.get(User, fb.user_id)
        appt = db.get(Appointment, fb.appointment_id)
        item.user_name = user.name if user else ""
        item.user_phone = user.phone if user else ""
        item.appointment_code = appt.code if appt else ""
        result.append(item)
    return result


@router.put("/admin/{feedback_id}/status", response_model=FeedbackOut)
def admin_update_status(
    feedback_id: int,
    data: FeedbackStatusIn,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if data.status not in FEEDBACK_STATUSES:
        raise HTTPException(status_code=400, detail="非法状态")
    fb = db.get(Feedback, feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="反馈不存在")
    fb.status = data.status
    fb.result = data.result
    db.commit()
    db.refresh(fb)
    return fb
