from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.constants import (
    ORG_TYPES,
    ROLE_LABELS,
    ROLE_PERMISSIONS,
    STAFF_ROLES,
)
from app.core.database import get_db
from app.core.deps import get_current_admin
from app.core.security import hash_password
from app.models import Organization, SysParam, User
from app.schemas import (
    OrgIn,
    OrgOut,
    PasswordResetIn,
    RoleOut,
    StaffIn,
    StaffOut,
    StaffUpdateIn,
    SysParamIn,
    SysParamOut,
)

router = APIRouter(prefix="/system", tags=["系统管理"])


# ---------- 组织机构 ----------
@router.get("/orgs", response_model=list[OrgOut])
def list_orgs(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Organization).order_by(Organization.id).all()


@router.get("/org-types")
def org_types(_: User = Depends(get_current_admin)):
    return ORG_TYPES


@router.post("/orgs", response_model=OrgOut)
def create_org(
    data: OrgIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    org = Organization(**data.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    record_audit(db, admin, "新增组织机构", org.name)
    return org


@router.put("/orgs/{org_id}", response_model=OrgOut)
def update_org(
    org_id: int,
    data: OrgIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="机构不存在")
    for k, v in data.model_dump().items():
        setattr(org, k, v)
    db.commit()
    db.refresh(org)
    record_audit(db, admin, "修改组织机构", org.name)
    return org


@router.delete("/orgs/{org_id}")
def delete_org(
    org_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="机构不存在")
    db.delete(org)
    db.commit()
    record_audit(db, admin, "删除组织机构", org.name)
    return {"message": "已删除"}


# ---------- 用户管理（工作人员账号） ----------
def _staff_out(u: User) -> StaffOut:
    item = StaffOut.model_validate(u)
    item.role_label = ROLE_LABELS.get(u.role, u.role)
    return item


@router.get("/staff", response_model=list[StaffOut])
def list_staff(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = (
        db.query(User)
        .filter(User.role.in_(STAFF_ROLES))
        .order_by(User.id)
        .all()
    )
    return [_staff_out(u) for u in rows]


@router.post("/staff", response_model=StaffOut)
def create_staff(
    data: StaffIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if data.role not in STAFF_ROLES:
        raise HTTPException(status_code=400, detail="非法的工作人员角色")
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(status_code=400, detail="该手机号/账号已存在")
    user = User(
        name=data.name,
        phone=data.phone,
        password=hash_password(data.password),
        role=data.role,
        dept=data.dept,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    record_audit(db, admin, "新增工作人员", user.name, user.role)
    return _staff_out(user)


@router.put("/staff/{user_id}", response_model=StaffOut)
def update_staff(
    user_id: int,
    data: StaffUpdateIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if data.role not in STAFF_ROLES:
        raise HTTPException(status_code=400, detail="非法的工作人员角色")
    user = db.get(User, user_id)
    if not user or user.role not in STAFF_ROLES:
        raise HTTPException(status_code=404, detail="工作人员不存在")
    user.name = data.name
    user.role = data.role
    user.dept = data.dept
    user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    record_audit(db, admin, "修改工作人员", user.name)
    return _staff_out(user)


@router.post("/staff/{user_id}/reset-password")
def reset_password(
    user_id: int,
    data: PasswordResetIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.password = hash_password(data.password)
    db.commit()
    record_audit(db, admin, "重置密码", user.name)
    return {"message": "密码已重置"}


@router.delete("/staff/{user_id}")
def delete_staff(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user or user.role not in STAFF_ROLES:
        raise HTTPException(status_code=404, detail="工作人员不存在")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录账号")
    record_audit(db, admin, "删除工作人员", user.name)
    db.delete(user)
    db.commit()
    return {"message": "已删除"}


# ---------- 角色权限 ----------
@router.get("/roles", response_model=list[RoleOut])
def list_roles(_: User = Depends(get_current_admin)):
    return [
        RoleOut(role=r, label=ROLE_LABELS.get(r, r), permissions=perms)
        for r, perms in ROLE_PERMISSIONS.items()
    ]


# ---------- 系统参数 ----------
@router.get("/params", response_model=list[SysParamOut])
def list_params(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(SysParam).order_by(SysParam.id).all()


@router.put("/params/{param_id}", response_model=SysParamOut)
def update_param(
    param_id: int,
    data: SysParamIn,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    param = db.get(SysParam, param_id)
    if not param:
        raise HTTPException(status_code=404, detail="参数不存在")
    param.value = data.value
    db.commit()
    db.refresh(param)
    record_audit(db, admin, "修改系统参数", param.key, data.value)
    return param
