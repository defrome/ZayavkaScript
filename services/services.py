from typing import Dict, Any

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

    def create_services(self, name: str, description: str, price: int, photo_url: str) -> Dict[str, any]:

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

            service = Service(name=name, description=description, price=price, photo_url=photo_url)
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
                    "price": service.price,
                    "photo": service.photo_url
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

    def get_all_services(self) -> Dict[str, Any]:
        """
        Получить все услуги из базы данных (самый простой способ)
        """
        try:

            services = self.db.query(Service).all()

            services_list = [
                {
                    "id": service.id,
                    "name": service.name,
                    "description": service.description,
                    "price": service.price,
                    "photo": service.photo_url
                }
                for service in services
            ]

            return {
                "success": True,
                "count": len(services_list),
                "data": services_list
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении услуг: {str(e)}"
            )

    def get_service_by_id(self, service_id: int) -> Dict[str, Any]:
        """
        Получить услугу по ID
        """
        try:
            service = self.db.query(Service).filter(Service.id == service_id).first()

            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Услуга с ID {service_id} не найдена"
                )

            return {
                "success": True,
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении услуги: {str(e)}"
            )

