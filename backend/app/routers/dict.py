from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models import Dictionary, User
from app.schemas import DictIn, DictOut

router = APIRouter(prefix="/dicts", tags=["选项字典"])


@router.get("", response_model=list[DictOut])
def list_dicts(
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """获取选项字典，可按分类筛选。供前端下拉框使用，无需登录。"""
    q = db.query(Dictionary).filter(Dictionary.is_active.is_(True))
    if category:
        q = q.filter(Dictionary.category == category)
    return q.order_by(Dictionary.category, Dictionary.sort).all()


@router.get("/admin/list", response_model=list[DictOut])
def admin_list(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return db.query(Dictionary).order_by(Dictionary.category, Dictionary.sort).all()


@router.post("/admin", response_model=DictOut)
def create_dict(
    data: DictIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = Dictionary(
        category=data.category,
        label=data.label,
        value=data.value or data.label,
        sort=data.sort,
        is_active=data.is_active,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    record_audit(db, admin, "新增字典", f"{data.category}:{data.label}")
    return item


@router.put("/admin/{dict_id}", response_model=DictOut)
def update_dict(
    dict_id: int,
    data: DictIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = db.get(Dictionary, dict_id)
    if not item:
        raise HTTPException(status_code=404, detail="字典项不存在")
    item.category = data.category
    item.label = data.label
    item.value = data.value or data.label
    item.sort = data.sort
    item.is_active = data.is_active
    db.commit()
    db.refresh(item)
    record_audit(db, admin, "修改字典", f"{data.category}:{data.label}")
    return item


@router.delete("/admin/{dict_id}")
def delete_dict(
    dict_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = db.get(Dictionary, dict_id)
    if not item:
        raise HTTPException(status_code=404, detail="字典项不存在")
    db.delete(item)
    db.commit()
    record_audit(db, admin, "删除字典", f"{item.category}:{item.label}")
    return {"message": "已删除"}
