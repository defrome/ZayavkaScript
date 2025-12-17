from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any

from models.masters import Master, MasterTime


class MasterService:
    """
    Сервис для работы с мастерами
    """

    def __init__(self, db: Session):
        """
        Инициализация сервиса

        Args:
            db: Сессия базы данных
        """
        self.db = db

    def add_time_to_master(self, master_id: int, time_slot: str) -> Dict[str, Any]:
        """
        Добавить временной слот мастеру

        Args:
            master_id: ID мастера
            time_slot: Временной слот (например, "14:00")

        Returns:
            dict: Информация о добавленном времени
        """
        try:
            master = self.db.query(Master).filter(Master.id == master_id).first()
            if not master:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Мастер с id {master_id} не найден"
                )

            import re
            time_pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
            if not re.match(time_pattern, time_slot):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неверный формат времени. Используйте HH:MM (например, 14:30)"
                )

            existing_time = self.db.query(MasterTime).filter(
                MasterTime.time_slot == time_slot
            ).first()

            if existing_time:
                if existing_time in master.times:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Время '{time_slot}' уже добавлено этому мастеру"
                    )
                time_obj = existing_time
            else:

                time_obj = MasterTime(time_slot=time_slot)
                self.db.add(time_obj)
                self.db.commit()
                self.db.refresh(time_obj)

            if time_obj not in master.times:
                master.times.append(time_obj)
                self.db.commit()
                self.db.refresh(time_obj)

            return {
                "success": True,
                "message": "Время успешно добавлено мастеру",
                "data": {
                    "id": time_obj.id,
                    "time_slot": time_obj.time_slot,
                    "master_id": master_id
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

    def get_master_times(self, master_id: int) -> Dict[str, Any]:
        """
        Получить все времена мастера

        Args:
            master_id: ID мастера

        Returns:
            dict: Список времен мастера
        """
        master = self.db.query(Master).filter(Master.id == master_id).first()
        if not master:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Мастер с id {master_id} не найден"
            )

        times = [
            {
                "id": time.id,
                "time_slot": time.time_slot
            }
            for time in master.times
        ]

        return {
            "success": True,
            "master_id": master_id,
            "master_name": master.name,
            "times": times,
            "count": len(times)
        }

    def remove_time_from_master(self, master_id: int, time_slot_id: int) -> Dict[str, Any]:
        """
        Удалить время у мастера

        Args:
            master_id: ID мастера
            time_slot_id: ID временного слота

        Returns:
            dict: Результат операции
        """
        try:
            master = self.db.query(Master).filter(Master.id == master_id).first()
            time_obj = self.db.query(MasterTime).filter(MasterTime.id == time_slot_id).first()

            if not master:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Мастер с id {master_id} не найден"
                )

            if not time_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Время с id {time_slot_id} не найдено"
                )

            if time_obj not in master.times:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Время не принадлежит этому мастеру"
                )

            master.times.remove(time_obj)
            self.db.commit()

            return {
                "success": True,
                "message": "Время успешно удалено у мастера",
                "master_id": master_id,
                "time_slot_id": time_slot_id
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при удалении времени: {str(e)}"
            )

    def create_master(self, name: str) -> Dict[str, Any]:
        """
        Создать нового мастера

        Args:
            name: Имя мастера

        Returns:
            dict: Информация о созданном мастере
        """
        try:
            if not name or len(name.strip()) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Имя мастера должно содержать минимум 2 символа"
                )

            name = name.strip()

            existing_master = self.db.query(Master).filter(
                Master.name.ilike(name)
            ).first()

            if existing_master:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Мастер с именем '{name}' уже существует"
                )

            master = Master(name=name)
            self.db.add(master)
            self.db.commit()
            self.db.refresh(master)

            return {
                "success": True,
                "message": "Мастер успешно создан",
                "data": {
                    "id": master.id,
                    "name": master.name
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