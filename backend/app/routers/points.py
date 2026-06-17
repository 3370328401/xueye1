from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.constants import EXCHANGE_STATUSES
from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_staff, get_current_user
from app.core.points import add_points, get_balance
from app.models import Exchange, Gift, PointRecord, User
from app.schemas import (
    AdminExchangeOut,
    ExchangeIn,
    ExchangeOut,
    ExchangeStatusIn,
    GiftIn,
    GiftOut,
    PointRecordOut,
    PointSummaryOut,
)

router = APIRouter(prefix="/points", tags=["积分兑换"])


# ---------- 积分账户 ----------
@router.get("/mine", response_model=PointSummaryOut)
def my_points(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = (
        db.query(PointRecord)
        .filter(PointRecord.user_id == user.id)
        .order_by(PointRecord.id.desc())
        .all()
    )
    return PointSummaryOut(
        balance=get_balance(db, user.id),
        records=[PointRecordOut.model_validate(r) for r in records],
    )


# ---------- 礼品 ----------
@router.get("/gifts", response_model=list[GiftOut])
def list_gifts(db: Session = Depends(get_db)):
    return (
        db.query(Gift)
        .filter(Gift.is_active.is_(True))
        .order_by(Gift.points_cost)
        .all()
    )


@router.get("/gifts/admin/list", response_model=list[GiftOut])
def admin_gifts(_: User = Depends(get_current_staff), db: Session = Depends(get_db)):
    return db.query(Gift).order_by(Gift.id).all()


@router.post("/gifts", response_model=GiftOut)
def create_gift(
    data: GiftIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    gift = Gift(**data.model_dump())
    db.add(gift)
    db.commit()
    db.refresh(gift)
    record_audit(db, admin, "新增礼品", gift.name)
    return gift


@router.put("/gifts/{gift_id}", response_model=GiftOut)
def update_gift(
    gift_id: int,
    data: GiftIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    gift = db.get(Gift, gift_id)
    if not gift:
        raise HTTPException(status_code=404, detail="礼品不存在")
    for k, v in data.model_dump().items():
        setattr(gift, k, v)
    db.commit()
    db.refresh(gift)
    record_audit(db, admin, "修改礼品", gift.name)
    return gift


# ---------- 兑换 ----------
@router.post("/exchanges", response_model=ExchangeOut)
def create_exchange(
    data: ExchangeIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    gift = db.get(Gift, data.gift_id)
    if not gift or not gift.is_active:
        raise HTTPException(status_code=404, detail="礼品不存在或已下架")
    if gift.stock <= 0:
        raise HTTPException(status_code=400, detail="礼品库存不足")
    balance = get_balance(db, user.id)
    if balance < gift.points_cost:
        raise HTTPException(status_code=400, detail="积分不足，无法兑换")

    gift.stock -= 1
    add_points(db, user, -gift.points_cost, f"兑换礼品-{gift.name}", f"gift:{gift.id}")
    exchange = Exchange(
        user_id=user.id,
        gift_id=gift.id,
        gift_name=gift.name,
        points_cost=gift.points_cost,
        status="待处理",
    )
    db.add(exchange)
    db.commit()
    db.refresh(exchange)
    return exchange


@router.get("/exchanges/mine", response_model=list[ExchangeOut])
def my_exchanges(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.query(Exchange)
        .filter(Exchange.user_id == user.id)
        .order_by(Exchange.id.desc())
        .all()
    )


@router.post("/exchanges/{exchange_id}/cancel", response_model=ExchangeOut)
def cancel_exchange(
    exchange_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exchange = db.get(Exchange, exchange_id)
    if not exchange or exchange.user_id != user.id:
        raise HTTPException(status_code=404, detail="兑换记录不存在")
    if exchange.status not in ("待处理", "处理中"):
        raise HTTPException(status_code=400, detail="当前状态不可取消")
    exchange.status = "已取消"
    gift = db.get(Gift, exchange.gift_id)
    if gift:
        gift.stock += 1
    add_points(db, user, exchange.points_cost, f"兑换取消退还-{exchange.gift_name}", f"refund:{exchange.id}")
    db.commit()
    db.refresh(exchange)
    return exchange


@router.get("/exchanges/admin/list", response_model=list[AdminExchangeOut])
def admin_exchanges(
    status: str | None = None,
    _: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    q = db.query(Exchange)
    if status:
        q = q.filter(Exchange.status == status)
    rows = q.order_by(Exchange.id.desc()).all()
    result = []
    for ex in rows:
        item = AdminExchangeOut.model_validate(ex)
        u = db.get(User, ex.user_id)
        item.user_name = u.name if u else ""
        item.user_phone = u.phone if u else ""
        result.append(item)
    return result


@router.put("/exchanges/{exchange_id}/status", response_model=ExchangeOut)
def update_exchange_status(
    exchange_id: int,
    data: ExchangeStatusIn,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    if data.status not in EXCHANGE_STATUSES:
        raise HTTPException(status_code=400, detail="非法的兑换状态")
    exchange = db.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="兑换记录不存在")
    exchange.status = data.status
    db.commit()
    db.refresh(exchange)
    record_audit(db, staff, "更新兑换状态", exchange.gift_name, data.status)
    return exchange
