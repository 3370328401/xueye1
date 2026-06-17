import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.constants import (
    APPT_COLLECTING,
    APPT_PENDING_FORM,
    APPT_WAIT_COLLECT,
    QUEUE_STATUSES,
)
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Appointment, ExternalLog, SignRecord, User
from app.schemas import AppointmentOut, QueueItemOut

router = APIRouter(tags=["现场叫号与预约提醒"])


@router.get("/queue", response_model=list[QueueItemOut])
def queue_display(
    location: str | None = Query(None),
    blood_type: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """现场叫号显示：按预约单产生时间排队，展示前方等待人数。"""
    today = date.today().isoformat()
    q = db.query(Appointment).filter(
        Appointment.appoint_date == today,
        Appointment.status.in_(QUEUE_STATUSES),
    )
    if location:
        q = q.filter(Appointment.location == location)
    if blood_type:
        q = q.filter(Appointment.blood_type == blood_type)
    appts = q.order_by(Appointment.created_at).all()

    items: list[QueueItemOut] = []
    waiting_ahead = 0
    for appt in appts:
        user = db.get(User, appt.user_id)
        name = user.name if user else ""
        masked = (name[0] + "*" * (len(name) - 1)) if len(name) > 1 else name
        items.append(
            QueueItemOut(
                code=appt.code,
                name=masked,
                blood_type=appt.blood_type,
                status=appt.status,
                ahead=0 if appt.status == APPT_COLLECTING else waiting_ahead,
            )
        )
        if appt.status == APPT_WAIT_COLLECT:
            waiting_ahead += 1
    return items


@router.get("/reminders/mine", response_model=list[AppointmentOut])
def my_reminders(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """个人端预约提醒：展示未完成的、即将到来的预约。"""
    today = date.today().isoformat()
    return (
        db.query(Appointment)
        .filter(
            Appointment.user_id == user.id,
            Appointment.appoint_date >= today,
            Appointment.status.in_([APPT_PENDING_FORM, APPT_WAIT_COLLECT]),
        )
        .order_by(Appointment.appoint_date)
        .all()
    )


@router.post("/reminders/send/{appointment_id}")
def send_reminder(
    appointment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """触发预约提醒（模拟微信公众号模板消息推送）。"""
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="预约不存在")
    target = db.get(User, appt.user_id)
    signed = (
        db.query(SignRecord)
        .filter(SignRecord.appointment_id == appt.id)
        .count()
        > 0
    )
    content = {
        "to": target.phone if target else "",
        "appoint_date": appt.appoint_date,
        "time_slot": appt.time_slot,
        "location": appt.location,
        "double_form_signed": signed,
        "tips": "请按时到达采血点，携带身份证；如未完成双表签署请提前完成。",
    }
    resp = {"code": 0, "message": "模拟提醒推送成功", "channel": "wechat_template"}
    db.add(
        ExternalLog(
            api_type="reminder",
            request=json.dumps(content, ensure_ascii=False),
            response=json.dumps(resp, ensure_ascii=False),
            status="success",
        )
    )
    db.commit()
    return {"message": "预约提醒已发送（模拟）", "detail": content}
