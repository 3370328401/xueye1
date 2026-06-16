from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Location
from app.schemas import LocationOut

router = APIRouter(tags=["公共"])


@router.get("/ping")
def ping():
    return {"message": "pong", "service": "xueye-backend"}


@router.get("/locations", response_model=list[LocationOut])
def list_locations(db: Session = Depends(get_db)):
    return db.query(Location).filter(Location.is_active.is_(True)).all()
