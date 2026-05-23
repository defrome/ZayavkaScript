from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database.db import get_db
from database.redis_client import get_cache, set_cache, delete_cache
from models import Master, MasterTime
from schemas.masters import MasterCreate, MasterTimeCreate, MasterListResponse
from services.masters import MasterService
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/masters", tags=["masters"])

@router.get("/", response_model=MasterListResponse)
def get_all_masters(db: Session = Depends(get_db)):
    cache_key = "all_masters"
    cached_masters = get_cache(cache_key)

    if cached_masters:
        return {"status": "success", "data": cached_masters, "source": "cache"}

    masters = db.query(Master).options(joinedload(Master.times)).all()

    masters_json = jsonable_encoder(masters)
    set_cache(cache_key, masters_json)

    return {"status": "success", "data": masters, "source": "db"}

@router.get("/{master_id}/times/", response_model=Dict[str, Any])
def get_master_times(master_id: int, db: Session = Depends(get_db)):
    cache_key = f"master_times_{master_id}"
    cached_times = get_cache(cache_key)

    if cached_times:
        return {"status": "success", "data": cached_times, "source": "cache"}

    master = db.query(Master).options(joinedload(Master.times)).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Мастер с id {master_id} не найден",
        )
    result = [
        {
            "id": slot.id,
            "day": slot.day,
            "time_slot": slot.time_slot,
            "is_available": slot.is_available,
        }
        for slot in master.times
    ]

    set_cache(cache_key, jsonable_encoder(result))

    return {"status": "success", "data": result, "source": "db"}

@router.post("/create/", response_model=Dict[str, Any])
def create_master(payload: MasterCreate, db: Session = Depends(get_db)):
    master_service = MasterService(db)
    result = master_service.create_master(payload.name)

    delete_cache("all_masters")

    return result


@router.post("/{master_id}/times/")
def add_timeslot_to_specific_master(master_id: int, time_slot_data: MasterTimeCreate, db: Session = Depends(get_db)):
    master_service = MasterService(db)

    slot = master_service.add_time_to_master(
        master_id=master_id,
        day=time_slot_data.day,
        time_slot=time_slot_data.time_slot
    )

    updated_master = master_service.get_master(master_id)
    updated_times = [
        {
            "id": slot_item.id,
            "day": slot_item.day,
            "time_slot": slot_item.time_slot,
            "is_available": slot_item.is_available,
        }
        for slot_item in updated_master.times
    ]

    cache_key = f"master_times_{master_id}"
    set_cache(cache_key, jsonable_encoder(updated_times))

    delete_cache("all_masters")

    return {
        "status": "success",
        "data": {
            "id": slot.id,
            "master_id": slot.master_id,
            "day": slot.day,
            "time_slot": slot.time_slot,
            "is_available": slot.is_available,
        },
    }

@router.delete("/{master_id}/times/{time_slot_id}/", response_model=Dict[str, Any])
def remove_time_from_master(
        master_id: int,
        time_slot_id: int,
        db: Session = Depends(get_db)
):
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Мастер с id {master_id} не найден",
        )

    slot = db.query(MasterTime).filter(MasterTime.id == time_slot_id, MasterTime.master_id == master_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Слот {time_slot_id} для мастера {master_id} не найден",
        )

    db.delete(slot)
    db.commit()

    delete_cache(f"master_times_{master_id}")
    delete_cache("all_masters")

    return {"status": "success", "message": "Слот удален"}
