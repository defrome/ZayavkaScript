from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database.db import get_db
from database.redis_client import get_cache, set_cache, delete_cache
from models import Master, MasterTime
from schemas.masters import MasterResponse, MasterTimeCreate, MasterListEnvelope
from services.masters import MasterService
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/masters", tags=["masters"])


# --- ЧТЕНИЕ (GET) ---

@router.get("/", response_model=MasterListEnvelope)
def get_all_masters(db: Session = Depends(get_db)):
    cache_key = "all_masters"
    cached_masters = get_cache(cache_key)

    if cached_masters:
        return {"status": "success", "data": cached_masters, "source": "cache"}

    # Подгружаем связанные тайм-слоты сразу (eager loading)
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

    master_service = MasterService(db)
    result = master_service.get_master_times(master_id)

    # Сохраняем в кэш результат (даже если он пустой список)
    set_cache(cache_key, jsonable_encoder(result))

    return {"status": "success", "data": result, "source": "db"}


# --- ЗАПИСЬ И ИЗМЕНЕНИЕ (POST/DELETE) ---

@router.post("/create/", response_model=Dict[str, Any])
def create_master(name: str = Form(...), db: Session = Depends(get_db)):
    master_service = MasterService(db)
    result = master_service.create_master(name)

    # Инвалидация: список всех мастеров изменился
    delete_cache("all_masters")

    return result


@router.post("/{master_id}/times/", response_model=Dict[str, Any])
def add_timeslot_to_specific_master(
        master_id: int,
        time_slot_data: MasterTimeCreate,
        db: Session = Depends(get_db)
):
    master_service = MasterService(db)
    result = master_service.add_time_to_master(
        master_id=master_id,
        time_slot=time_slot_data.time_slot
    )

    # Очищаем кэш конкретного мастера и общий список
    delete_cache(f"master_times_{master_id}")
    delete_cache("all_masters")

    return result


@router.delete("/{master_id}/times/{time_slot_id}/", response_model=Dict[str, Any])
def remove_time_from_master(
        master_id: int,
        time_slot_id: int,
        db: Session = Depends(get_db)
):
    master_service = MasterService(db)
    result = master_service.remove_time_from_master(master_id, time_slot_id)

    # После удаления времени кэш должен быть обновлен
    delete_cache(f"master_times_{master_id}")
    delete_cache("all_masters")

    return result