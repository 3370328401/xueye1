import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import APPT_COLLECTED
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.points import get_balance
from app.models import Appointment, ExternalLog, User
from app.schemas import (
    BloodTestOut,
    DonationTraceOut,
    PersonalInfoOut,
)

router = APIRouter(prefix="/personal", tags=["个人信息查询(嵌入)"])

_VOLUME = {"全血": 400, "成分血": 200}


@router.get("/info", response_model=PersonalInfoOut)
def personal_info(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """嵌入展示个人献血相关信息（模拟采供血/微信公众号数据 + 平台已有数据）。"""
    done = (
        db.query(Appointment)
        .filter(
            Appointment.user_id == user.id,
            Appointment.status == APPT_COLLECTED,
        )
        .order_by(Appointment.appoint_date.desc())
        .all()
    )

    traces: list[DonationTraceOut] = []
    tests: list[BloodTestOut] = []
    total = 0
    for i, appt in enumerate(done, start=1):
        vol = _VOLUME.get(appt.blood_type, 300)
        total += vol
        traces.append(
            DonationTraceOut(
                seq=i,
                donate_date=appt.appoint_date,
                location=appt.location,
                volume_ml=vol,
                blood_type=appt.blood_type,
                identity="个人献血者",
            )
        )
        tests.append(
            BloodTestOut(
                seq=i,
                test_date=appt.appoint_date,
                result="合格",
                detail="HBsAg 阴性 / ALT 正常 / 抗-HCV 阴性 / 抗-HIV 阴性 / 梅毒 阴性",
            )
        )

    # 若无平台真实记录，补充来自采供血系统的模拟历史
    if not traces:
        traces = [
            DonationTraceOut(
                seq=1,
                donate_date="2024-03-12",
                location="市中心血站",
                volume_ml=400,
                blood_type="全血",
                identity="个人献血者",
            )
        ]
        tests = [
            BloodTestOut(
                seq=1,
                test_date="2024-03-12",
                result="合格",
                detail="（来自采供血业务管理系统-模拟）",
            )
        ]
        total = 400

    resp = PersonalInfoOut(
        e_cert_no=f"DXZ{user.id:08d}",
        total_volume_ml=total,
        donate_count=len(traces),
        points_balance=get_balance(db, user.id),
        blood_usage=[
            {"date": "2024-04-01", "hospital": "省人民医院", "usage": "临床用血 200ml"},
        ],
        tests=tests,
        traces=traces,
    )

    db.add(
        ExternalLog(
            api_type="blood_system_query",
            request=json.dumps({"user_id": user.id}, ensure_ascii=False),
            response=json.dumps(
                {"code": 0, "donate_count": len(traces)}, ensure_ascii=False
            ),
            status="success",
        )
    )
    db.commit()
    return resp
