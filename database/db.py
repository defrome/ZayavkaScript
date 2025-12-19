from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine("sqlite:////app/applications.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autoflush=False, bind=engine)

class Base(DeclarativeBase): pass

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Все таблицы БД созданы")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()