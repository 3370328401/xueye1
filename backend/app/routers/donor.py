from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import DonorInfo, User
from app.schemas import DonorInfoIn, DonorInfoOut

router = APIRouter(prefix="/donor", tags=["献血者信息"])


@router.get("/info", response_model=DonorInfoOut | None)
def get_info(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(DonorInfo).filter(DonorInfo.user_id == user.id).first()


@router.post("/info", response_model=DonorInfoOut)
def upsert_info(
    data: DonorInfoIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    info = db.query(DonorInfo).filter(DonorInfo.user_id == user.id).first()
    if info is None:
        info = DonorInfo(user_id=user.id)
        db.add(info)
    for field, value in data.model_dump().items():
        setattr(info, field, value)
    db.commit()
    db.refresh(info)
    return info
