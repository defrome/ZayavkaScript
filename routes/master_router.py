from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database.db import get_db
from models import Master, MasterTime
from schemas.masters import MasterResponse, MasterTimeCreate
from services.masters import MasterService

router = APIRouter(prefix="/masters", tags=["masters"])

@router.get("/", response_model=List[MasterResponse])
def get_all_masters(
        db: Session = Depends(get_db)
):
    """
    Получить список всех мастеров с их расписанием
    """
    masters = db.query(Master).all()

    return masters


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