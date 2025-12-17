from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.services import Service


class ServicesService:

    def __init__(self, db: Session):
        """
        Инициализация сервиса

        Args:
            db: Сессия базы данных
        """
        self.db = db

    def create_services(self, name: str, description: str, price: int) -> Dict[str, any]:

        try:
            if not name or len(name.strip()) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Имя услуги должно содержать минимум 2 символа"
                )

            name = name.strip()

            existing_service = self.db.query(Service).filter(
                Service.name.ilike(name)
            ).first()

            if existing_service:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Услуга с названием '{name}' уже существует"
                )

            service = Service(name=name, description=description, price=price)
            self.db.add(service)
            self.db.commit()
            self.db.refresh(service)

            return {
                "success": True,
                "message": "Услуга успешна создана",
                "data": {
                    "id": service.id,
                    "name": service.name,
                    "description": service.description,
                    "price": service.price
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка сервера: {str(e)}"
            )

