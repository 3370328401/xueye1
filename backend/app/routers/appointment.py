import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_user
from app.models import Appointment, User
from app.schemas import (
    AdminAppointmentOut,
    AppointmentIn,
    AppointmentOut,
    AppointmentStatusIn,
)

router = APIRouter(prefix="/appointments", tags=["预约"])

APPOINTMENT_STATUSES = [
    "待填写健康征询表",
    "已填写健康征询表",
    "待现场采血",
    "正在现场采血",
    "已完成现场采血",
    "已取消",
    "作废",
]


def gen_code() -> str:
    return "YY" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(10, 99))


@router.post("", response_model=AppointmentOut)
def create_appointment(
    data: AppointmentIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appt = Appointment(
        code=gen_code(),
        user_id=user.id,
        blood_type=data.blood_type,
        appoint_date=data.appoint_date,
        time_slot=data.time_slot,
        location=data.location,
        remark=data.remark,
        status="待填写健康征询表",
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@router.get("/mine", response_model=list[AppointmentOut])
def my_appointments(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.query(Appointment)
        .filter(Appointment.user_id == user.id)
        .order_by(Appointment.created_at.desc())
        .all()
    )


@router.get("/{appointment_id}", response_model=AppointmentOut)
def appointment_detail(
    appointment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="预约不存在")
    if appt.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="无权查看")
    return appt


@router.post("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_appointment(
    appointment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="预约不存在")
    if appt.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    appt.status = "已取消"
    db.commit()
    db.refresh(appt)
    return appt


# ---------- Admin ----------
@router.get("/admin/list", response_model=list[AdminAppointmentOut])
def admin_list(
    name: str | None = Query(None),
    phone: str | None = Query(None),
    appoint_date: str | None = Query(None),
    blood_type: str | None = Query(None),
    status: str | None = Query(None),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    q = db.query(Appointment).join(User, Appointment.user_id == User.id)
    if name:
        q = q.filter(User.name.like(f"%{name}%"))
    if phone:
        q = q.filter(User.phone.like(f"%{phone}%"))
    if appoint_date:
        q = q.filter(Appointment.appoint_date == appoint_date)
    if blood_type:
        q = q.filter(Appointment.blood_type == blood_type)
    if status:
        q = q.filter(Appointment.status == status)
    rows = q.order_by(Appointment.created_at.desc()).all()
    result = []
    for appt in rows:
        item = AdminAppointmentOut.model_validate(appt)
        item.user_name = appt.user.name
        item.user_phone = appt.user.phone
        result.append(item)
    return result


@router.put("/admin/{appointment_id}/status", response_model=AppointmentOut)
def admin_update_status(
    appointment_id: int,
    data: AppointmentStatusIn,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if data.status not in APPOINTMENT_STATUSES:
        raise HTTPException(status_code=400, detail="非法状态")
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="预约不存在")
    appt.status = data.status
    db.commit()
    db.refresh(appt)
    return appt
