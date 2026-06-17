from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models import AuditLog, User
from app.schemas import AuditLogOut

router = APIRouter(prefix="/audit-logs", tags=["操作日志"])


@router.get("", response_model=list[AuditLogOut])
def list_logs(
    action: str | None = Query(None),
    keyword: str | None = Query(None),
    limit: int = Query(200, le=1000),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            (AuditLog.user_name.like(like))
            | (AuditLog.target.like(like))
            | (AuditLog.detail.like(like))
        )
    return q.order_by(AuditLog.created_at.desc()).limit(limit).all()
