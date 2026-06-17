from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.constants import ROLE_COLLECTOR
from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models import BloodPlan, GroupActivity, StaffShift, User
from app.schemas import (
    BloodPlanOut,
    BloodPlanUpdate,
    PlanGenerateIn,
    ShiftGenerateIn,
    StaffShiftOut,
    StaffShiftUpdate,
)

router = APIRouter(prefix="/schedules", tags=["排班计划"])

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def _weekday(date_str: str) -> str:
    try:
        return WEEKDAYS[date.fromisoformat(date_str[:10]).weekday()]
    except ValueError:
        return ""


def _in_range(date_str: str, start: str, end: str) -> bool:
    try:
        d = date.fromisoformat(date_str[:10])
        return date.fromisoformat(start) <= d <= date.fromisoformat(end)
    except ValueError:
        return False


# ---------- 团体献血计划 ----------
@router.post("/blood-plans/generate", response_model=list[BloodPlanOut])
def generate_blood_plans(
    data: PlanGenerateIn,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """根据团体活动自动生成指定区间的团体献血周/月计划。"""
    activities = db.query(GroupActivity).all()
    created = []
    for a in activities:
        if not a.activity_date or not _in_range(a.activity_date, data.start_date, data.end_date):
            continue
        exists = (
            db.query(BloodPlan)
            .filter(
                BloodPlan.activity_id == a.id,
                BloodPlan.plan_type == data.plan_type,
            )
            .first()
        )
        if exists:
            continue
        plan = BloodPlan(
            plan_type=data.plan_type,
            activity_id=a.id,
            plan_date=a.activity_date,
            weekday=_weekday(a.activity_date),
            location=a.location,
            unit_name=a.unit_name,
            contact_phone=a.contact_phone,
            expected_count=a.expected_count,
            arrive_time="08:30",
        )
        db.add(plan)
        created.append(plan)
    db.commit()
    for p in created:
        db.refresh(p)
    record_audit(db, staff, "生成团体献血计划", f"{data.plan_type}计划", f"{len(created)}条")
    return created


@router.get("/blood-plans/admin/list", response_model=list[BloodPlanOut])
def blood_plans_list(
    plan_type: str | None = Query(None),
    status: str | None = Query(None),
    unit_name: str | None = Query(None),
    _: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    q = db.query(BloodPlan)
    if plan_type:
        q = q.filter(BloodPlan.plan_type == plan_type)
    if status:
        q = q.filter(BloodPlan.status == status)
    if unit_name:
        q = q.filter(BloodPlan.unit_name.like(f"%{unit_name}%"))
    return q.order_by(BloodPlan.plan_date).all()


@router.put("/blood-plans/{plan_id}", response_model=BloodPlanOut)
def update_blood_plan(
    plan_id: int,
    data: BloodPlanUpdate,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    plan = db.get(BloodPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    if data.plan_date:
        plan.plan_date = data.plan_date
        plan.weekday = _weekday(data.plan_date)
    if data.location:
        plan.location = data.location
    if data.expected_count:
        plan.expected_count = data.expected_count
    if data.arrive_time:
        plan.arrive_time = data.arrive_time
    plan.remark = data.remark or plan.remark
    db.commit()
    db.refresh(plan)
    record_audit(db, staff, "修改团体献血计划", plan.unit_name)
    return plan


@router.post("/blood-plans/{plan_id}/publish", response_model=BloodPlanOut)
def publish_blood_plan(
    plan_id: int,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    plan = db.get(BloodPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    plan.status = "已发布"
    db.commit()
    db.refresh(plan)
    record_audit(db, staff, "发布团体献血计划", plan.unit_name)
    return plan


@router.get("/blood-plans/query", response_model=list[BloodPlanOut])
def blood_plans_query(phone: str = Query(...), db: Session = Depends(get_db)):
    """团体单位联系人查看本单位已发布的献血计划。"""
    return (
        db.query(BloodPlan)
        .filter(BloodPlan.contact_phone == phone, BloodPlan.status == "已发布")
        .order_by(BloodPlan.plan_date)
        .all()
    )


# ---------- 体采人员排班 ----------
@router.post("/staff-shifts/generate", response_model=list[StaffShiftOut])
def generate_shifts(
    data: ShiftGenerateIn,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """根据区间内团体活动与可用体采人员自动生成排班表。"""
    collectors = (
        db.query(User)
        .filter(User.role == ROLE_COLLECTOR, User.is_active.is_(True))
        .all()
    )
    names = [c.name for c in collectors] or ["体采科-李干事"]
    activities = [
        a
        for a in db.query(GroupActivity).all()
        if a.activity_date and _in_range(a.activity_date, data.start_date, data.end_date)
    ]
    created = []
    for idx, a in enumerate(activities):
        exists = (
            db.query(StaffShift)
            .filter(
                StaffShift.shift_date == a.activity_date,
                StaffShift.location == a.location,
            )
            .first()
        )
        if exists:
            continue
        # 简单按需分配人数：每 20 预约人数 1 名采血人员，至少 2 名
        need = max(2, -(-a.expected_count // 20))
        assigned = [names[(idx + i) % len(names)] for i in range(min(need, len(names)))]
        mobile = "流动采血" in a.location or "车" in a.location
        shift = StaffShift(
            shift="全天",
            shift_date=a.activity_date,
            weekday=_weekday(a.activity_date),
            location=a.location,
            expected_count=a.expected_count,
            staff_names="、".join(assigned),
            start_time="08:00",
            end_time="17:00",
            vehicle="流动采血车 琼A·12345" if mobile else "",
            driver="王师傅" if mobile else "",
            notice="请提前 30 分钟到岗，做好物资准备",
        )
        db.add(shift)
        created.append(shift)
    db.commit()
    for s in created:
        db.refresh(s)
    record_audit(db, staff, "生成体采排班", f"{data.start_date}~{data.end_date}", f"{len(created)}条")
    return created


@router.get("/staff-shifts/admin/list", response_model=list[StaffShiftOut])
def shifts_list(
    staff_name: str | None = Query(None),
    location: str | None = Query(None),
    vehicle: str | None = Query(None),
    status: str | None = Query(None),
    _: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    q = db.query(StaffShift)
    if staff_name:
        q = q.filter(StaffShift.staff_names.like(f"%{staff_name}%"))
    if location:
        q = q.filter(StaffShift.location.like(f"%{location}%"))
    if vehicle:
        q = q.filter(StaffShift.vehicle.like(f"%{vehicle}%"))
    if status:
        q = q.filter(StaffShift.status == status)
    return q.order_by(StaffShift.shift_date).all()


@router.put("/staff-shifts/{shift_id}", response_model=StaffShiftOut)
def update_shift(
    shift_id: int,
    data: StaffShiftUpdate,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    shift = db.get(StaffShift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="排班不存在")
    shift.shift = data.shift or shift.shift
    shift.staff_names = data.staff_names or shift.staff_names
    shift.start_time = data.start_time or shift.start_time
    shift.end_time = data.end_time or shift.end_time
    shift.vehicle = data.vehicle if data.vehicle != "" else shift.vehicle
    shift.driver = data.driver if data.driver != "" else shift.driver
    shift.notice = data.notice or shift.notice
    db.commit()
    db.refresh(shift)
    record_audit(db, staff, "修改体采排班", shift.location)
    return shift


@router.post("/staff-shifts/{shift_id}/publish", response_model=StaffShiftOut)
def publish_shift(
    shift_id: int,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    shift = db.get(StaffShift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="排班不存在")
    shift.status = "已发布"
    db.commit()
    db.refresh(shift)
    record_audit(db, staff, "发布体采排班", shift.location)
    return shift
