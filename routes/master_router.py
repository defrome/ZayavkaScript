from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database.db import get_db
from database.redis_client import get_cache, set_cache
from models import Master, MasterTime
from schemas.masters import MasterResponse, MasterTimeCreate, MasterListEnvelope
from services.masters import MasterService

router = APIRouter(prefix="/masters", tags=["masters"])

from fastapi.encoders import jsonable_encoder


@router.get("/", response_model=MasterListEnvelope)
def get_all_masters(db: Session = Depends(get_db)):
    cached_masters = get_cache("all_masters")
    if cached_masters:
        return {"status": "success", "data": cached_masters, "source": "cache"}

    masters = db.query(Master).all()

    masters_json = jsonable_encoder(masters)

    set_cache("all_masters", masters_json)

    return {
        "status": "success",
        "data": masters,
        "source": "db"
    }


@router.get("/{master_id}/times/", response_model=Dict[str, Any])
def get_master_times(
    master_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить все времена мастера
    """
    master_service = MasterService(db)
    return master_service.get_master_times(master_id)


@router.delete("/{master_id}/times/{time_slot_id}/", response_model=Dict[str, Any])
def remove_time_from_master(
    master_id: int,
    time_slot_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить время у мастера
    """
    master_service = MasterService(db)
    return master_service.remove_time_from_master(master_id, time_slot_id)


@router.post("/create/", response_model=Dict[str, Any])
def create_master(
        name: str = Form(...),
        db: Session = Depends(get_db)
):
    """
    Создать мастера парикмахера
    """
    master_service = MasterService(db)

    result = master_service.create_master(name)

    return result


@router.post("/{master_id}/times/", response_model=Dict[str, Any])
def add_timeslot_to_specific_master(
        master_id: int,
        time_slot_data: MasterTimeCreate,
        db: Session = Depends(get_db)
):
    """
    Добавить временной слот мастеру
    """
    master_service = MasterService(db)

    result = master_service.add_time_to_master(
        master_id=master_id,
        time_slot=time_slot_data.time_slot
    )

    return result