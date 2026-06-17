import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.constants import (
    MESSAGE_SCOPES,
    MESSAGE_STATUSES,
    MESSAGE_TYPES,
    ROLE_DONOR,
)
from app.core.database import get_db
from app.core.deps import get_current_staff, get_current_user
from app.models import ExternalLog, Message, MessageRead, User
from app.schemas import (
    AdminMessageOut,
    MessageIn,
    MessageOut,
    UserMessageOut,
)

router = APIRouter(prefix="/messages", tags=["消息推送"])


def _target_match(user: User, target: dict) -> bool:
    """定向推送筛选：按用户类型/地区等条件匹配。"""
    if not target:
        return True
    roles = target.get("roles")
    if roles and user.role not in roles:
        return False
    phones = target.get("phones")
    if phones and user.phone not in phones:
        return False
    return True


# ---------- 管理端 ----------
@router.post("", response_model=MessageOut)
def create_message(
    data: MessageIn,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    msg = Message(
        title=data.title,
        content=data.content,
        msg_type=data.msg_type,
        scope=data.scope,
        target=json.dumps(data.target, ensure_ascii=False),
        status="草稿",
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    record_audit(db, staff, "新增消息", data.title)
    return msg


@router.put("/{msg_id}", response_model=MessageOut)
def update_message(
    msg_id: int,
    data: MessageIn,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    msg = db.get(Message, msg_id)
    if not msg:
        raise HTTPException(status_code=404, detail="消息不存在")
    if msg.status == "已发布":
        raise HTTPException(status_code=400, detail="已发布消息不可编辑，请先撤回")
    msg.title = data.title
    msg.content = data.content
    msg.msg_type = data.msg_type
    msg.scope = data.scope
    msg.target = json.dumps(data.target, ensure_ascii=False)
    db.commit()
    db.refresh(msg)
    record_audit(db, staff, "修改消息", data.title)
    return msg


@router.post("/{msg_id}/publish", response_model=MessageOut)
def publish_message(
    msg_id: int,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    msg = db.get(Message, msg_id)
    if not msg:
        raise HTTPException(status_code=404, detail="消息不存在")
    msg.status = "已发布"
    msg.published_at = datetime.now()

    # 模拟微信公众号群发/模板消息推送，记录外部调用日志
    target = json.loads(msg.target or "{}")
    recipients = [
        u
        for u in db.query(User).filter(User.role == ROLE_DONOR).all()
        if msg.scope == "普发" or _target_match(u, target)
    ]
    db.add(
        ExternalLog(
            api_type="wechat_push",
            request=json.dumps(
                {"title": msg.title, "scope": msg.scope, "target": target},
                ensure_ascii=False,
            ),
            response=json.dumps(
                {"code": 0, "pushed_count": len(recipients)}, ensure_ascii=False
            ),
            status="success",
        )
    )
    db.commit()
    db.refresh(msg)
    record_audit(db, staff, "发布消息", msg.title, f"推送 {len(recipients)} 人")
    return msg


@router.post("/{msg_id}/revoke", response_model=MessageOut)
def revoke_message(
    msg_id: int,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    msg = db.get(Message, msg_id)
    if not msg:
        raise HTTPException(status_code=404, detail="消息不存在")
    msg.status = "已撤回"
    db.commit()
    db.refresh(msg)
    record_audit(db, staff, "撤回消息", msg.title)
    return msg


@router.delete("/{msg_id}")
def delete_message(
    msg_id: int,
    staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    msg = db.get(Message, msg_id)
    if not msg:
        raise HTTPException(status_code=404, detail="消息不存在")
    db.query(MessageRead).filter(MessageRead.message_id == msg_id).delete()
    db.delete(msg)
    db.commit()
    record_audit(db, staff, "删除消息", msg.title)
    return {"message": "已删除"}


@router.get("/admin/list", response_model=list[AdminMessageOut])
def admin_list(
    _: User = Depends(get_current_staff), db: Session = Depends(get_db)
):
    rows = db.query(Message).order_by(Message.id.desc()).all()
    result = []
    for m in rows:
        item = AdminMessageOut.model_validate(m)
        item.read_count = (
            db.query(MessageRead).filter(MessageRead.message_id == m.id).count()
        )
        result.append(item)
    return result


@router.get("/meta")
def message_meta(_: User = Depends(get_current_staff)):
    return {
        "types": MESSAGE_TYPES,
        "scopes": MESSAGE_SCOPES,
        "statuses": MESSAGE_STATUSES,
    }


# ---------- 个人端 ----------
@router.get("/mine", response_model=list[UserMessageOut])
def my_messages(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    msgs = (
        db.query(Message)
        .filter(Message.status == "已发布")
        .order_by(Message.published_at.desc())
        .all()
    )
    read_ids = {
        r.message_id
        for r in db.query(MessageRead).filter(MessageRead.user_id == user.id).all()
    }
    result = []
    for m in msgs:
        target = json.loads(m.target or "{}")
        if m.scope == "定向" and not _target_match(user, target):
            continue
        item = UserMessageOut.model_validate(m)
        item.is_read = m.id in read_ids
        result.append(item)
    return result


@router.post("/{msg_id}/read")
def mark_read(
    msg_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    msg = db.get(Message, msg_id)
    if not msg:
        raise HTTPException(status_code=404, detail="消息不存在")
    exists = (
        db.query(MessageRead)
        .filter(MessageRead.message_id == msg_id, MessageRead.user_id == user.id)
        .first()
    )
    if not exists:
        db.add(MessageRead(message_id=msg_id, user_id=user.id))
        db.commit()
    return {"message": "已读"}
