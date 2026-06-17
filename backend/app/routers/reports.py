import csv
import io
from collections import Counter

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models import (
    Appointment,
    Evaluation,
    Feedback,
    GroupActivity,
    Message,
    MessageRead,
    StaffShift,
    User,
)

router = APIRouter(prefix="/reports", tags=["统计报表导出"])


def _csv_response(filename: str, headers: list[str], rows: list[list]):
    buf = io.StringIO()
    buf.write("\ufeff")  # UTF-8 BOM, 便于 Excel 正确显示中文
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/appointments.csv")
def export_appointments(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    rows = []
    for a in db.query(Appointment).order_by(Appointment.id).all():
        u = db.get(User, a.user_id)
        rows.append(
            [
                a.code,
                u.name if u else "",
                u.phone if u else "",
                a.blood_type,
                a.appoint_date,
                a.time_slot,
                a.location,
                a.status,
            ]
        )
    return _csv_response(
        "appointments.csv",
        ["业务流程号", "姓名", "手机号", "献血类型", "预约日期", "时段", "采血地点", "状态"],
        rows,
    )


@router.get("/groups.csv")
def export_groups(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    rows = [
        [
            g.flow_no,
            g.unit_name,
            g.unit_type,
            g.contact_name,
            g.contact_phone,
            g.activity_date,
            g.actual_date or "",
            g.location,
            g.expected_count,
            g.actual_count,
            g.year,
        ]
        for g in db.query(GroupActivity).order_by(GroupActivity.id).all()
    ]
    return _csv_response(
        "groups.csv",
        ["流程号", "单位名称", "单位类型", "联系人", "联系电话", "活动日期", "实际献血日期", "采血地点", "预约人数", "实际人数", "年度"],
        rows,
    )


@router.get("/shifts.csv")
def export_shifts(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    rows = [
        [
            s.shift_date,
            s.weekday,
            s.shift,
            s.location,
            s.expected_count,
            s.staff_names,
            s.start_time,
            s.end_time,
            s.vehicle,
            s.driver,
            s.status,
        ]
        for s in db.query(StaffShift).order_by(StaffShift.id).all()
    ]
    return _csv_response(
        "shifts.csv",
        ["日期", "星期", "班次", "点位", "预约人数", "工作人员", "上班时间", "下班时间", "车辆", "司机", "状态"],
        rows,
    )


@router.get("/evaluations.csv")
def export_evaluations(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    rows = []
    for e in db.query(Evaluation).order_by(Evaluation.id).all():
        u = db.get(User, e.user_id)
        rows.append(
            [
                u.name if u else "",
                e.env_score,
                e.attitude_score,
                e.wait_score,
                e.skill_score,
                e.notice_score,
                e.overall_score,
                e.suggestion,
                e.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )
    return _csv_response(
        "evaluations.csv",
        ["姓名", "采血环境", "工作人员态度", "等待时间", "业务技能", "注意事项讲解", "总体", "改进建议", "提交时间"],
        rows,
    )


@router.get("/feedbacks.csv")
def export_feedbacks(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    rows = []
    for f in db.query(Feedback).order_by(Feedback.id).all():
        u = db.get(User, f.user_id)
        types = []
        if f.swelling:
            types.append("肿包")
        if f.redness:
            types.append("发红")
        if f.arm_pain:
            types.append("手臂疼痛")
        rows.append(
            [
                u.name if u else "",
                u.phone if u else "",
                "、".join(types) or "其他",
                f.other_desc,
                f.status,
                f.result,
                f.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )
    return _csv_response(
        "feedbacks.csv",
        ["姓名", "手机号", "异常类型", "其他描述", "处理状态", "处理结果", "反馈时间"],
        rows,
    )


@router.get("/messages.csv")
def export_messages(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    rows = []
    for m in db.query(Message).order_by(Message.id).all():
        read_count = (
            db.query(MessageRead).filter(MessageRead.message_id == m.id).count()
        )
        rows.append(
            [
                m.title,
                m.msg_type,
                m.scope,
                m.status,
                read_count,
                m.published_at.strftime("%Y-%m-%d %H:%M") if m.published_at else "",
            ]
        )
    return _csv_response(
        "messages.csv",
        ["标题", "类型", "范围", "状态", "已读数", "发布时间"],
        rows,
    )


@router.get("/summary")
def report_summary(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    """报表汇总：各报表条数与若干关键指标。"""
    appts = db.query(Appointment).all()
    evals = db.query(Evaluation).all()
    avg_overall = (
        round(sum(e.overall_score for e in evals) / len(evals), 2) if evals else 0
    )
    return {
        "appointment_total": len(appts),
        "appointment_by_status": dict(Counter(a.status for a in appts)),
        "group_total": db.query(GroupActivity).count(),
        "shift_total": db.query(StaffShift).count(),
        "evaluation_total": len(evals),
        "evaluation_avg_overall": avg_overall,
        "feedback_total": db.query(Feedback).count(),
        "message_total": db.query(Message).count(),
    }
