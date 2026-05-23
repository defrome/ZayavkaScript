from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from models.masters import Master, MasterTime


class MasterService:
    def __init__(self, db: Session):
        self.db = db

    def list_masters(self, active_only: bool = True) -> list[Master]:
        query = self.db.query(Master).options(selectinload(Master.times))
        if active_only:
            query = query.filter(Master.is_active.is_(True))
        return query.order_by(Master.name.asc()).all()

    def get_master(self, master_id: int) -> Master:
        master = (
            self.db.query(Master)
            .options(selectinload(Master.times))
            .filter(Master.id == master_id)
            .first()
        )
        if not master:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Мастер с id {master_id} не найден",
            )
        return master

    def create_master(self, name: str) -> Master:
        cleaned_name = name.strip()
        existing = self.db.query(Master).filter(Master.name.ilike(cleaned_name)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Мастер с именем '{cleaned_name}' уже существует",
            )

        master = Master(name=cleaned_name, is_active=True)
        self.db.add(master)
        self.db.commit()
        self.db.refresh(master)
        return master

    def add_time_to_master(self, master_id: int, day: date, time_slot: str) -> MasterTime:
        master = self.get_master(master_id)

        duplicate_slot = (
            self.db.query(MasterTime)
            .filter(
                MasterTime.master_id == master.id,
                MasterTime.day == day,
                MasterTime.time_slot == time_slot,
            )
            .first()
        )
        if duplicate_slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Слот {time_slot} на {day.isoformat()} уже существует",
            )

        slot = MasterTime(master_id=master.id, day=day, time_slot=time_slot, is_available=True)
        self.db.add(slot)
        self.db.commit()
        self.db.refresh(slot)
        return slot
