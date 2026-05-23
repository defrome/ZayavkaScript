from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.services import Service


class ServicesService:
    def __init__(self, db: Session):
        self.db = db

    def list_services(self, active_only: bool = True) -> list[Service]:
        query = self.db.query(Service)
        if active_only:
            query = query.filter(Service.is_active.is_(True))
        return query.order_by(Service.name.asc()).all()

    def get_service(self, service_id: int) -> Service:
        service = self.db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Услуга с ID {service_id} не найдена",
            )
        return service

    def create_service(self, name: str, description: str | None, price: int, photo_url: str | None) -> Service:
        name = name.strip()

        duplicate = self.db.query(Service).filter(Service.name.ilike(name)).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Услуга с названием '{name}' уже существует",
            )

        service = Service(
            name=name,
            description=description,
            price=price,
            photo_url=photo_url,
            is_active=True,
        )
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service
