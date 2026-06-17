from sqlalchemy.orm import Session

from app.models import PointRecord, User


def get_balance(db: Session, user_id: int) -> int:
    last = (
        db.query(PointRecord)
        .filter(PointRecord.user_id == user_id)
        .order_by(PointRecord.id.desc())
        .first()
    )
    return last.balance_after if last else 0


def add_points(
    db: Session, user: User, change: int, reason: str, ref: str = ""
) -> PointRecord:
    balance = get_balance(db, user.id) + change
    record = PointRecord(
        user_id=user.id,
        change=change,
        balance_after=balance,
        reason=reason,
        ref=ref,
    )
    db.add(record)
    db.flush()
    return record


def has_ref(db: Session, user_id: int, ref: str) -> bool:
    return (
        db.query(PointRecord)
        .filter(PointRecord.user_id == user_id, PointRecord.ref == ref)
        .first()
        is not None
    )
