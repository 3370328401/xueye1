import random
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.constants import GROUP_STATUSES, UNIT_TYPES
from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models import GroupActivity, GroupApplication, User
from app.schemas import (
    GroupActivityIn,
    GroupActivityOut,
    GroupActivityUpdate,
    GroupApplicationIn,
    GroupApplicationOut,
    GroupStatusIn,
)

router = APIRouter(prefix="/group-applications", tags=["团体申报"])


def gen_flow_no() -> str:
    return "TT" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(10, 99))


@router.post("", response_model=GroupApplicationOut)
def create_application(data: GroupApplicationIn, db: Session = Depends(get_db)):
    unit_type = data.unit_type if data.unit_type in UNIT_TYPES else "其他"
    app_row = GroupApplication(
        unit_name=data.unit_name,
        credit_code=data.credit_code,
        unit_address=data.unit_address,
        contact_name=data.contact_name,
        contact_phone=data.contact_phone,
        unit_type=unit_type,
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
def admin_list(
    unit_type: str | None = Query(None),
    status: str | None = Query(None),
    _: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    q = db.query(GroupApplication)
    if unit_type:
        q = q.filter(GroupApplication.unit_type == unit_type)
    if status:
        q = q.filter(GroupApplication.status == status)
    return q.order_by(GroupApplication.created_at.desc()).all()


@router.put("/admin/{app_id}/status", response_model=GroupApplicationOut)
def admin_update_status(
    app_id: int,
    data: GroupStatusIn,
    staff: User = Depends(get_current_staff),
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
    record_audit(db, staff, "团体申报受理", row.unit_name, data.status)
    return row


# ---------- 团体献血活动 ----------
@router.post("/activities", response_model=GroupActivityOut)
def create_activity(
    data: GroupActivityIn,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    unit_type = data.unit_type if data.unit_type in UNIT_TYPES else "其他"
    if data.application_id:
        app_row = db.get(GroupApplication, data.application_id)
        if not app_row:
            raise HTTPException(status_code=404, detail="关联的团体申报不存在")
        unit_type = app_row.unit_type
    year = 0
    if data.activity_date:
        try:
            year = int(data.activity_date[:4])
        except ValueError:
            year = 0
    activity = GroupActivity(
        flow_no=gen_flow_no(),
        application_id=data.application_id,
        unit_name=data.unit_name,
        unit_type=unit_type,
        contact_name=data.contact_name,
        contact_phone=data.contact_phone,
        center_contact=data.center_contact,
        activity_date=data.activity_date,
        location=data.location,
        expected_count=data.expected_count,
        year=year,
        remark=data.remark,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    record_audit(db, staff, "创建团体活动", activity.unit_name, activity.flow_no)
    return activity


@router.get("/activities/query", response_model=list[GroupActivityOut])
def activities_by_phone(phone: str = Query(...), db: Session = Depends(get_db)):
    return (
        db.query(GroupActivity)
        .filter(GroupActivity.contact_phone == phone)
        .order_by(GroupActivity.created_at.desc())
        .all()
    )


@router.get("/activities/admin/list", response_model=list[GroupActivityOut])
def activities_admin_list(
    year: int | None = Query(None),
    unit_type: str | None = Query(None),
    unit_name: str | None = Query(None),
    _: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    q = db.query(GroupActivity)
    if year:
        q = q.filter(GroupActivity.year == year)
    if unit_type:
        q = q.filter(GroupActivity.unit_type == unit_type)
    if unit_name:
        q = q.filter(GroupActivity.unit_name.like(f"%{unit_name}%"))
    return q.order_by(GroupActivity.created_at.desc()).all()


@router.put("/activities/admin/{activity_id}", response_model=GroupActivityOut)
def update_activity(
    activity_id: int,
    data: GroupActivityUpdate,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    activity = db.get(GroupActivity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    activity.actual_date = data.actual_date or activity.actual_date
    activity.actual_count = data.actual_count or activity.actual_count
    activity.center_contact = data.center_contact or activity.center_contact
    activity.remark = data.remark or activity.remark
    db.commit()
    db.refresh(activity)
    record_audit(db, staff, "更新团体活动", activity.unit_name, activity.flow_no)
    return activity


# ---------- 团体统计 ----------
@router.get("/stats/by-type")
def stats_by_type(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    """按单位类型统计团体活动数量、预约/实际人数。"""
    activities = db.query(GroupActivity).all()
    agg = {t: {"activities": 0, "expected": 0, "actual": 0} for t in UNIT_TYPES}
    for a in activities:
        key = a.unit_type if a.unit_type in agg else "其他"
        agg[key]["activities"] += 1
        agg[key]["expected"] += a.expected_count
        agg[key]["actual"] += a.actual_count
    return [
        {"unit_type": t, **agg[t]} for t in UNIT_TYPES
    ]


@router.get("/stats/by-year")
def stats_by_year(
    year: int | None = Query(None),
    _: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """按年度汇总团体献血情况；指定 year 时返回该年各单位明细。"""
    q = db.query(GroupActivity)
    if year:
        rows = q.filter(GroupActivity.year == year).all()
        agg = defaultdict(lambda: {"activities": 0, "expected": 0, "actual": 0})
        for a in rows:
            agg[a.unit_name]["activities"] += 1
            agg[a.unit_name]["expected"] += a.expected_count
            agg[a.unit_name]["actual"] += a.actual_count
        return [{"unit_name": k, **v} for k, v in agg.items()]
    rows = q.all()
    agg = defaultdict(lambda: {"activities": 0, "expected": 0, "actual": 0})
    for a in rows:
        y = a.year or 0
        agg[y]["activities"] += 1
        agg[y]["expected"] += a.expected_count
        agg[y]["actual"] += a.actual_count
    return [{"year": k, **v} for k, v in sorted(agg.items())]
