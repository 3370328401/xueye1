import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models import ExternalLog, User
from app.schemas import ExternalLogOut

router = APIRouter(prefix="/external", tags=["外部系统占位接口"])


class ExternalRequest(BaseModel):
    payload: dict = {}


def _log(db: Session, api_type: str, request: dict, response: dict):
    db.add(
        ExternalLog(
            api_type=api_type,
            request=json.dumps(request, ensure_ascii=False),
            response=json.dumps(response, ensure_ascii=False),
            status="success",
        )
    )
    db.commit()


@router.post("/e-sign")
def e_sign(data: ExternalRequest, db: Session = Depends(get_db)):
    """无纸化签署服务接口占位"""
    resp = {
        "code": 0,
        "message": "模拟签署成功",
        "sign_id": "MOCK-SIGN-0001",
        "note": "MVP 阶段使用'本人确认信息真实有效'代替真实电子签名",
    }
    _log(db, "e_sign", data.payload, resp)
    return resp


@router.post("/blood-system")
def blood_system(data: ExternalRequest, db: Session = Depends(get_db)):
    """采供血业务管理系统接口占位"""
    resp = {
        "code": 0,
        "message": "模拟采供血系统返回",
        "donate_history": [
            {"date": "2024-03-12", "blood_type": "全血", "volume_ml": 400},
            {"date": "2023-09-08", "blood_type": "成分血", "volume_ml": 200},
        ],
        "last_donate_date": "2024-03-12",
        "test_result": {"hbsag": "阴性", "alt": "正常", "result": "合格"},
    }
    _log(db, "blood_system", data.payload, resp)
    return resp


@router.post("/wechat")
def wechat(data: ExternalRequest, db: Session = Depends(get_db)):
    """微信公众号接口占位"""
    resp = {
        "code": 0,
        "message": "暂未接入真实微信授权",
        "openid": "MOCK-OPENID-0001",
        "note": "MVP 阶段返回模拟登录结果",
    }
    _log(db, "wechat", data.payload, resp)
    return resp


@router.post("/recruit-call")
def recruit_call(data: ExternalRequest, db: Session = Depends(get_db)):
    """智慧招募呼叫管理接口占位"""
    resp = {
        "code": 0,
        "message": "模拟推送成功",
        "pushed_count": len(data.payload.get("donors", [])) or 1,
        "note": "MVP 阶段不做真实推送，仅返回模拟结果",
    }
    _log(db, "recruit_call", data.payload, resp)
    return resp


@router.get("/logs", response_model=list[ExternalLogOut])
def list_logs(_: User = Depends(get_current_staff), db: Session = Depends(get_db)):
    return (
        db.query(ExternalLog)
        .order_by(ExternalLog.created_at.desc())
        .limit(100)
        .all()
    )
