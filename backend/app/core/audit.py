"""操作日志记录工具。"""

from sqlalchemy.orm import Session

from app.models import AuditLog, User


def record_audit(
    db: Session,
    user: User | None,
    action: str,
    target: str = "",
    detail: str = "",
    commit: bool = True,
) -> None:
    log = AuditLog(
        user_id=user.id if user else None,
        user_name=user.name if user else "",
        role=user.role if user else "",
        action=action,
        target=target,
        detail=detail,
    )
    db.add(log)
    if commit:
        db.commit()
