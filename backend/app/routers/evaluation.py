import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_staff, get_current_user
from app.core.points import add_points, has_ref
from app.models import Appointment, EvalTemplate, Evaluation, User
from app.schemas import (
    AdminEvaluationOut,
    EvalTemplateIn,
    EvalTemplateOut,
    EvaluationIn,
    EvaluationOut,
)

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

    # 评价送积分：同一次献血仅奖励一次
    ref = f"eval:{data.appointment_id}"
    if not has_ref(db, user.id, ref):
        tpl = (
            db.query(EvalTemplate)
            .filter(
                EvalTemplate.blood_type == (appt.blood_type or "全血"),
                EvalTemplate.is_active.is_(True),
            )
            .first()
        )
        reward = tpl.reward_points if tpl else 20
        add_points(db, user, reward, "献血评价奖励", ref)

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


# ---------- 评价模板管理 ----------
@router.get("/templates", response_model=list[EvalTemplateOut])
def list_templates(
    blood_type: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(EvalTemplate).filter(EvalTemplate.is_active.is_(True))
    if blood_type:
        q = q.filter(EvalTemplate.blood_type == blood_type)
    return q.order_by(EvalTemplate.id).all()


@router.get("/templates/admin/list", response_model=list[EvalTemplateOut])
def admin_templates(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    return db.query(EvalTemplate).order_by(EvalTemplate.id).all()


@router.post("/templates", response_model=EvalTemplateOut)
def create_template(
    data: EvalTemplateIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    tpl = EvalTemplate(
        name=data.name,
        blood_type=data.blood_type,
        indicators=json.dumps(data.indicators, ensure_ascii=False),
        reward_points=data.reward_points,
        is_active=data.is_active,
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    record_audit(db, admin, "新增评价模板", tpl.name)
    return tpl


@router.put("/templates/{tpl_id}", response_model=EvalTemplateOut)
def update_template(
    tpl_id: int,
    data: EvalTemplateIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    tpl = db.get(EvalTemplate, tpl_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    tpl.name = data.name
    tpl.blood_type = data.blood_type
    tpl.indicators = json.dumps(data.indicators, ensure_ascii=False)
    tpl.reward_points = data.reward_points
    tpl.is_active = data.is_active
    db.commit()
    db.refresh(tpl)
    record_audit(db, admin, "修改评价模板", tpl.name)
    return tpl
