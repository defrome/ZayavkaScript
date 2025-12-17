from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from models import Master, MasterTime
from schemas.masters import MasterResponse, MasterTimeCreate, MasterTimeResponse

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


@router.post("/create/", response_model=MasterResponse)
def create_master(
        name: str = Form(...),
        db: Session = Depends(get_db)
):
    """
    Создать мастера парикмахера
    """
    existing_master = db.query(Master).filter(Master.name == name).first()
    if existing_master:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Мастер с именем '{name}' уже существует"
        )

    master = Master(name=name)
    db.add(master)
    db.commit()
    db.refresh(master)

    return master


@router.post("/{master_id}/times/", response_model=MasterTimeResponse)
def add_timeslot_to_specific_master(
        master_id: int,
        time_slot_data: MasterTimeCreate,
        db: Session = Depends(get_db)
):
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Мастер с id {master_id} не найден"
        )
    existing_time = db.query(MasterTime).filter(
        MasterTime.time_slot == time_slot_data.time_slot
    ).first()

    if existing_time:
        if existing_time in master.times:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Время '{time_slot_data.time_slot}' уже добавлено этому мастеру"
            )
        time_obj = existing_time

    else:
        time_obj = MasterTime(time_slot=time_slot_data.time_slot)
        db.add(time_obj)
        db.commit()
        db.refresh(time_obj)

    try:
        master.times.append(time_obj)
        db.commit()
        db.refresh(time_obj)

        return time_obj

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при связывании времени с мастером: {str(e)}"
        )