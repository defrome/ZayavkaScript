from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from models import Master
from schemas.masters import MasterResponse

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

    # Проверяем, существует ли уже мастер с таким именем
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