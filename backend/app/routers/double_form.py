import json
import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.constants import (
    APPT_FORM_DONE,
    APPT_PENDING_FORM,
    APPT_WAIT_COLLECT,
    FORM_HEALTH,
    FORM_PERSONAL,
    SIGN_DONE,
)
from app.core.database import get_db
from app.core.deps import get_current_staff, get_current_user
from app.models import (
    Appointment,
    DonorInfo,
    ExternalLog,
    HealthSurvey,
    SignRecord,
    User,
)
from app.schemas import SignIn, SignRecordOut

router = APIRouter(prefix="/double-forms", tags=["双表与电子签署"])


def _personal_form(donor: DonorInfo, appt: Appointment) -> dict:
    return {
        "姓名": donor.name,
        "身份证号": donor.id_card,
        "性别": donor.gender,
        "年龄": donor.age,
        "职业": donor.occupation,
        "手机号": donor.phone,
        "联系地址": donor.address,
        "紧急联系人": donor.emergency_contact,
        "紧急联系电话": donor.emergency_phone,
        "预约编号": appt.code,
        "献血类型": appt.blood_type,
        "预约日期": appt.appoint_date,
        "采血地点": appt.location,
    }


def _health_form(survey: HealthSurvey) -> dict:
    yn = lambda v: "是" if v else "否"
    return {
        "当前身体状况良好": yn(survey.is_healthy),
        "24小时内是否饮酒": yn(survey.drank_alcohol),
        "近期是否服药": yn(survey.took_medicine),
        "是否有感冒发热等症状": yn(survey.has_symptoms),
        "是否有重大疾病史": yn(survey.has_major_disease),
        "是否存在不宜献血情况": yn(survey.unsuitable),
        "其他说明": survey.other_note or "无",
        "本人确认信息真实有效": yn(survey.confirmed),
    }


def _build_forms(db: Session, user: User, appointment_id: int):
    appt = db.get(Appointment, appointment_id)
    if not appt or appt.user_id != user.id:
        raise HTTPException(status_code=404, detail="预约不存在")
    donor = db.query(DonorInfo).filter(DonorInfo.user_id == user.id).first()
    if not donor or not donor.name or not donor.id_card:
        raise HTTPException(status_code=400, detail="请先在「个人信息」中完善基本信息")
    survey = (
        db.query(HealthSurvey)
        .filter(
            HealthSurvey.user_id == user.id,
            HealthSurvey.appointment_id == appointment_id,
        )
        .order_by(HealthSurvey.created_at.desc())
        .first()
    )
    if not survey:
        raise HTTPException(status_code=400, detail="请先填写该预约的健康征询表")
    return appt, donor, survey


@router.get("/preview")
def preview(
    appointment_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据个人信息 + 健康征询 + 预约自动生成双表预览。"""
    appt, donor, survey = _build_forms(db, user, appointment_id)
    signed = (
        db.query(SignRecord)
        .filter(
            SignRecord.appointment_id == appointment_id,
            SignRecord.user_id == user.id,
        )
        .count()
        > 0
    )
    return {
        "appointment_id": appt.id,
        "appointment_code": appt.code,
        "status": appt.status,
        "signed": signed,
        "forms": [
            {"form_name": FORM_PERSONAL, "fields": _personal_form(donor, appt)},
            {"form_name": FORM_HEALTH, "fields": _health_form(survey)},
        ],
    }


@router.post("/sign", response_model=list[SignRecordOut])
def sign(
    data: SignIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not data.confirmed:
        raise HTTPException(status_code=400, detail="请确认双表内容真实无误后再签署")
    appt, donor, survey = _build_forms(db, user, data.appointment_id)
    if appt.status != APPT_PENDING_FORM:
        raise HTTPException(status_code=400, detail="当前预约状态不可签署双表")

    existed = (
        db.query(SignRecord)
        .filter(
            SignRecord.appointment_id == appt.id,
            SignRecord.user_id == user.id,
        )
        .first()
    )
    if existed:
        raise HTTPException(status_code=400, detail="该预约双表已签署")

    sign_no = "QS" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(10, 99))
    forms = [
        (FORM_PERSONAL, _personal_form(donor, appt)),
        (FORM_HEALTH, _health_form(survey)),
    ]
    records = []
    for name, fields in forms:
        rec = SignRecord(
            user_id=user.id,
            appointment_id=appt.id,
            form_name=name,
            status=SIGN_DONE,
            sign_no=sign_no,
            content=json.dumps(fields, ensure_ascii=False),
        )
        db.add(rec)
        records.append(rec)

    appt.status = APPT_FORM_DONE
    # 模拟调用无纸化签署服务
    db.add(
        ExternalLog(
            api_type="e_sign",
            request=f"appointment={appt.code}, signer={user.name}, signature={data.signature or '本人确认'}",
            response=f"模拟签署成功, 签署流水号={sign_no}",
            status="success",
        )
    )
    db.commit()
    for rec in records:
        db.refresh(rec)
    record_audit(db, user, "签署双表", appt.code, sign_no)
    return records


@router.get("/mine", response_model=list[SignRecordOut])
def my_signs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(SignRecord)
        .filter(SignRecord.user_id == user.id)
        .order_by(SignRecord.signed_at.desc())
        .all()
    )
    result = []
    for r in rows:
        item = SignRecordOut.model_validate(r)
        appt = db.get(Appointment, r.appointment_id)
        item.appointment_code = appt.code if appt else ""
        result.append(item)
    return result


@router.get("/admin/list", response_model=list[SignRecordOut])
def admin_list(
    appointment_code: str | None = Query(None),
    only_unverified: bool = Query(False),
    _: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    q = db.query(SignRecord)
    if only_unverified:
        q = q.filter(SignRecord.verified.is_(False))
    rows = q.order_by(SignRecord.signed_at.desc()).all()
    result = []
    for r in rows:
        appt = db.get(Appointment, r.appointment_id)
        if appointment_code and (not appt or appointment_code not in appt.code):
            continue
        item = SignRecordOut.model_validate(r)
        u = db.get(User, r.user_id)
        item.appointment_code = appt.code if appt else ""
        item.user_name = u.name if u else ""
        item.user_phone = u.phone if u else ""
        result.append(item)
    return result


@router.post("/admin/verify/{appointment_id}", response_model=list[SignRecordOut])
def verify(
    appointment_id: int,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """现场身份认证 + 双表审验通过，预约进入待现场采血。"""
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="预约不存在")
    records = (
        db.query(SignRecord)
        .filter(SignRecord.appointment_id == appointment_id)
        .all()
    )
    if not records:
        raise HTTPException(status_code=400, detail="该预约尚未签署双表，无法审验")
    if appt.status != APPT_FORM_DONE:
        raise HTTPException(
            status_code=400, detail=f"当前状态「{appt.status}」不可进行双表审验"
        )
    for r in records:
        r.verified = True
    appt.status = APPT_WAIT_COLLECT
    db.commit()
    out = []
    for r in records:
        db.refresh(r)
        item = SignRecordOut.model_validate(r)
        item.appointment_code = appt.code
        out.append(item)
    record_audit(db, staff, "双表审验通过", appt.code)
    return out
