from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_user
from app.models import Appointment, ExternalLog, HealthSurvey, User
from app.schemas import AdminHealthSurveyOut, HealthSurveyIn, HealthSurveyOut

router = APIRouter(prefix="/health-surveys", tags=["健康征询表"])


@router.post("", response_model=HealthSurveyOut)
def submit_survey(
    data: HealthSurveyIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appt = db.get(Appointment, data.appointment_id)
    if not appt or appt.user_id != user.id:
        raise HTTPException(status_code=404, detail="预约不存在")
    if not data.confirmed:
        raise HTTPException(status_code=400, detail="请确认信息真实有效")

    survey = HealthSurvey(
        appointment_id=data.appointment_id,
        user_id=user.id,
        is_healthy=data.is_healthy,
        drank_alcohol=data.drank_alcohol,
        took_medicine=data.took_medicine,
        has_symptoms=data.has_symptoms,
        has_major_disease=data.has_major_disease,
        unsuitable=data.unsuitable,
        other_note=data.other_note,
        confirmed=data.confirmed,
    )
    db.add(survey)
    if appt.status == "待填写健康征询表":
        appt.status = "已填写健康征询表"

    # 模拟无纸化签署服务调用：用"本人确认信息真实有效"代替真实电子签名
    db.add(
        ExternalLog(
            api_type="e_sign",
            request=f"appointment={appt.code}, confirmed={data.confirmed}",
            response="模拟签署成功",
            status="success",
        )
    )
    db.commit()
    db.refresh(survey)
    return survey


@router.get("/mine", response_model=list[HealthSurveyOut])
def my_surveys(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(HealthSurvey)
        .filter(HealthSurvey.user_id == user.id)
        .order_by(HealthSurvey.created_at.desc())
        .all()
    )


@router.get("/admin/list", response_model=list[AdminHealthSurveyOut])
def admin_list(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = db.query(HealthSurvey).order_by(HealthSurvey.created_at.desc()).all()
    result = []
    for s in rows:
        item = AdminHealthSurveyOut.model_validate(s)
        user = db.get(User, s.user_id)
        appt = db.get(Appointment, s.appointment_id)
        item.user_name = user.name if user else ""
        item.user_phone = user.phone if user else ""
        item.appointment_code = appt.code if appt else ""
        result.append(item)
    return result


@router.get("/admin/{survey_id}", response_model=AdminHealthSurveyOut)
def admin_detail(
    survey_id: int, _: User = Depends(get_current_admin), db: Session = Depends(get_db)
):
    s = db.get(HealthSurvey, survey_id)
    if not s:
        raise HTTPException(status_code=404, detail="记录不存在")
    item = AdminHealthSurveyOut.model_validate(s)
    user = db.get(User, s.user_id)
    appt = db.get(Appointment, s.appointment_id)
    item.user_name = user.name if user else ""
    item.user_phone = user.phone if user else ""
    item.appointment_code = appt.code if appt else ""
    return item
