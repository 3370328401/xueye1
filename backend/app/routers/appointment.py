import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.constants import (
    APPOINTMENT_STATUSES,
    APPT_PENDING_FORM,
    APPT_VOID,
    ROLE_ADMIN,
    can_transition,
)
from app.core.database import get_db
from app.core.deps import get_current_staff, get_current_user
from app.models import Appointment, User
from app.schemas import (
    AdminAppointmentOut,
    AppointmentIn,
    AppointmentOut,
    AppointmentStatusIn,
)

router = APIRouter(prefix="/appointments", tags=["预约"])


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
        status=APPT_PENDING_FORM,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    record_audit(db, user, "创建预约", appt.code, f"{data.blood_type} {data.appoint_date}")
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
    if appt.user_id != user.id and user.role == "user":
        raise HTTPException(status_code=403, detail="无权查看")
    return appt


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
    appointment_id: int,
    data: AppointmentIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """用户修改预约（仅限未进入现场采血流程的预约）。"""
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="预约不存在")
    if appt.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    if appt.status not in (APPT_PENDING_FORM,):
        raise HTTPException(status_code=400, detail="当前状态不允许修改预约")
    appt.blood_type = data.blood_type
    appt.appoint_date = data.appoint_date
    appt.time_slot = data.time_slot
    appt.location = data.location
    appt.remark = data.remark
    db.commit()
    db.refresh(appt)
    record_audit(db, user, "修改预约", appt.code)
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
    if appt.status in (APPT_VOID,):
        raise HTTPException(status_code=400, detail="预约已作废")
    appt.status = APPT_VOID
    db.commit()
    db.refresh(appt)
    record_audit(db, user, "取消预约", appt.code)
    return appt


# ---------- 工作人员 ----------
@router.get("/admin/list", response_model=list[AdminAppointmentOut])
def admin_list(
    name: str | None = Query(None),
    phone: str | None = Query(None),
    appoint_date: str | None = Query(None),
    blood_type: str | None = Query(None),
    location: str | None = Query(None),
    status: str | None = Query(None),
    _: User = Depends(get_current_staff),
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
    if location:
        q = q.filter(Appointment.location.like(f"%{location}%"))
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
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    if data.status not in APPOINTMENT_STATUSES:
        raise HTTPException(status_code=400, detail="非法状态")
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="预约不存在")
    # 系统管理员可强制修正状态；其他工作人员需遵循状态流转规则
    if staff.role != ROLE_ADMIN and appt.status != data.status:
        if not can_transition(appt.status, data.status):
            raise HTTPException(
                status_code=400,
                detail=f"不允许从「{appt.status}」流转到「{data.status}」",
            )
    old = appt.status
    appt.status = data.status
    db.commit()
    db.refresh(appt)
    record_audit(
        db, staff, "修改预约状态", appt.code, f"{old} -> {data.status}"
    )
    return appt
