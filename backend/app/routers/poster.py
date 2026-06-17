from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_staff
from app.models import ExternalLog, Poster, PosterTemplate, User
from app.schemas import PosterIn, PosterOut, PosterTemplateIn, PosterTemplateOut

router = APIRouter(prefix="/posters", tags=["宣传海报"])


# ---------- 模板（管理员维护）----------
@router.get("/templates", response_model=list[PosterTemplateOut])
def list_templates(_: User = Depends(get_current_staff), db: Session = Depends(get_db)):
    return (
        db.query(PosterTemplate)
        .filter(PosterTemplate.is_active.is_(True))
        .order_by(PosterTemplate.id)
        .all()
    )


@router.post("/templates", response_model=PosterTemplateOut)
def create_template(
    data: PosterTemplateIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    tpl = PosterTemplate(
        name=data.name,
        bg_color=data.bg_color,
        title_style=data.title_style,
        contact=data.contact,
        qrcode_text=data.qrcode_text,
        is_active=data.is_active,
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    record_audit(db, admin, "新增海报模板", tpl.name)
    return tpl


@router.put("/templates/{tpl_id}", response_model=PosterTemplateOut)
def update_template(
    tpl_id: int,
    data: PosterTemplateIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    tpl = db.get(PosterTemplate, tpl_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    tpl.name = data.name
    tpl.bg_color = data.bg_color
    tpl.title_style = data.title_style
    tpl.contact = data.contact
    tpl.qrcode_text = data.qrcode_text
    tpl.is_active = data.is_active
    db.commit()
    db.refresh(tpl)
    record_audit(db, admin, "修改海报模板", tpl.name)
    return tpl


# ---------- 海报生成 / 推送 ----------
@router.post("", response_model=PosterOut)
def create_poster(
    data: PosterIn,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    bg_color = data.bg_color
    contact = data.contact
    qrcode_text = data.qrcode_text
    if data.template_id:
        tpl = db.get(PosterTemplate, data.template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail="模板不存在")
        bg_color = bg_color or tpl.bg_color
        contact = contact or tpl.contact
        qrcode_text = qrcode_text or tpl.qrcode_text
    poster = Poster(
        template_id=data.template_id,
        unit_name=data.unit_name,
        contact_phone=data.contact_phone,
        title=data.title,
        activity_date=data.activity_date,
        location=data.location,
        bg_color=bg_color or "#c62828",
        contact=contact,
        qrcode_text=qrcode_text or f"献血预约-{data.unit_name}",
        status="草稿",
    )
    db.add(poster)
    db.commit()
    db.refresh(poster)
    record_audit(db, staff, "生成宣传海报", poster.unit_name)
    return poster


@router.get("/admin/list", response_model=list[PosterOut])
def admin_list(
    unit_name: str | None = Query(None),
    _: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    q = db.query(Poster)
    if unit_name:
        q = q.filter(Poster.unit_name.like(f"%{unit_name}%"))
    return q.order_by(Poster.created_at.desc()).all()


@router.post("/{poster_id}/push", response_model=PosterOut)
def push_poster(
    poster_id: int,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    poster = db.get(Poster, poster_id)
    if not poster:
        raise HTTPException(status_code=404, detail="海报不存在")
    poster.status = "已推送"
    poster.pushed_at = datetime.utcnow()
    # 模拟通过微信公众号推送给团体单位联系人
    db.add(
        ExternalLog(
            api_type="wechat",
            request=f"push_poster unit={poster.unit_name}, phone={poster.contact_phone}",
            response="模拟海报推送成功",
            status="success",
        )
    )
    db.commit()
    db.refresh(poster)
    record_audit(db, staff, "推送宣传海报", poster.unit_name)
    return poster


@router.get("/query", response_model=list[PosterOut])
def query_by_phone(phone: str = Query(...), db: Session = Depends(get_db)):
    """团体单位联系人查看本单位已推送的海报。"""
    return (
        db.query(Poster)
        .filter(Poster.contact_phone == phone, Poster.status == "已推送")
        .order_by(Poster.created_at.desc())
        .all()
    )
