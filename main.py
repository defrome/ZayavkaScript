from sqlalchemy.orm import Session
from database.db import engine, SessionLocal
from models.application import Base, Application
from models.masters import Master, MasterTime
from models.users import User

Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)
print("Все таблицы БД созданы заново")

def create_sample_data(db: Session, name, telephone_number, time_slot):

    user = User(name=name, telephone_number=telephone_number)
    db.add(user)

    master = Master(name="Мария Петрова")
    db.add(master)

    time1 = MasterTime(time_slot=time_slot)
    db.add(time1)

    db.commit()

    master.times.append(time1)

    db.commit()

    application = Application(
        service="Женская стрижка",
        price=6500,
        date="2024-01-20",
        user_id=user.id,
        master_id=master.id,
        time_id=time1.id
    )
    db.add(application)

    db.commit()

    db.refresh(application)
    db.refresh(user)
    db.refresh(master)
    db.refresh(time1)

    print(f"Пользователь {user.name} создал заявку на {application.service}")
    print(f"Мастер: {master.name}")
    print(f"Время: {time1.time_slot}")
    print(f"ID заявки: {application.id}")

try:
    db = SessionLocal()
    create_sample_data(db, "Илья", "+79774955636", "19:30")
    print("Данные успешно созданы")

finally:
    db.close()
    print("Сессия БД закрыта")