from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models import GroupApplication, User
from app.schemas import GroupApplicationIn, GroupApplicationOut, GroupStatusIn

router = APIRouter(prefix="/group-applications", tags=["团体申报"])

GROUP_STATUSES = ["待受理", "受理中", "受理已完成", "已驳回"]


@router.post("", response_model=GroupApplicationOut)
def create_application(data: GroupApplicationIn, db: Session = Depends(get_db)):
    app_row = GroupApplication(
        unit_name=data.unit_name,
        credit_code=data.credit_code,
        unit_address=data.unit_address,
        contact_name=data.contact_name,
        contact_phone=data.contact_phone,
        expected_count=data.expected_count,
        expected_date=data.expected_date,
        admin_remark=data.remark,
        status="待受理",
    )
    db.add(app_row)
    db.commit()
    db.refresh(app_row)
    return app_row


@router.get("/query", response_model=list[GroupApplicationOut])
def query_by_phone(phone: str = Query(...), db: Session = Depends(get_db)):
    return (
        db.query(GroupApplication)
        .filter(GroupApplication.contact_phone == phone)
        .order_by(GroupApplication.created_at.desc())
        .all()
    )


@router.get("/admin/list", response_model=list[GroupApplicationOut])
def admin_list(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return (
        db.query(GroupApplication)
        .order_by(GroupApplication.created_at.desc())
        .all()
    )


@router.put("/admin/{app_id}/status", response_model=GroupApplicationOut)
def admin_update_status(
    app_id: int,
    data: GroupStatusIn,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if data.status not in GROUP_STATUSES:
        raise HTTPException(status_code=400, detail="非法状态")
    row = db.get(GroupApplication, app_id)
    if not row:
        raise HTTPException(status_code=404, detail="申报不存在")
    row.status = data.status
    row.admin_remark = data.admin_remark
    db.commit()
    db.refresh(row)
    return row
