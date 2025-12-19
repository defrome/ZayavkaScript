from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any

from models.application import Application
from models.masters import Master, MasterTime
from models.users import User


class ApplicationService:

    def __init__(self, service: str, price: int, date: Optional[str] = None):
        """
        Инициализация сервиса создания заявок

        Args:
            service: Название услуги
            price: Цена услуги
            date: Дата заявки (если None - текущая дата)
        """
        self.service = service
        self.price = price
        self.date = date or datetime.now().strftime("%d/%m/%Y")

    @staticmethod
    def get_all_applications(db: Session):

        return db.query(Application).all()

    def create_application(self, db: Session, name: str, telephone_number: str,
                           time_slot: str, master_name: str) -> Dict[str, Any]:
        """
        Создание заявки с пользователем, мастером и временем

        Args:
            db: Сессия базы данных
            name: Имя пользователя
            telephone_number: Номер телефона пользователя
            time_slot: Временной слот (например, "14:00")
            master_name: Имя мастера

        Returns:
            dict: Информация о созданной заявке
        """
        try:

            user = User(name=name, telephone_number=telephone_number)
            db.add(user)

            master = db.query(Master).filter(Master.name == master_name).first()
            if not master:
                master = Master(name=master_name)
                db.add(master)

            time_obj = db.query(MasterTime).filter(MasterTime.time_slot == time_slot).first()
            if not time_obj:
                time_obj = MasterTime(time_slot=time_slot)
                db.add(time_obj)

            db.commit()

            if time_obj not in master.times:
                master.times.append(time_obj)
                db.commit()

            application = Application(
                service=self.service,
                price=self.price,
                date=self.date,
                user_id=user.id,
                master_id=master.id,
                time_id=time_obj.id
            )
            db.add(application)
            db.commit()

            db.refresh(application)
            db.refresh(user)
            db.refresh(master)
            db.refresh(time_obj)

            return {
                "success": True,
                "message": "Заявка успешно создана",
                "data": {
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "telephone_number": user.telephone_number
                    },
                    "master": {
                        "id": master.id,
                        "name": master.name
                    },
                    "time_slot": {
                        "id": time_obj.id,
                        "time_slot": time_obj.time_slot
                    },
                    "application": {
                        "id": application.id,
                        "service": application.service,
                        "price": application.price,
                        "date": application.date
                    }
                }
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Ошибка при создании заявки: {str(e)}"
            }