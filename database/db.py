import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

if os.path.exists("/.dockerenv") or os.environ.get("REDIS_HOST"):
    DATABASE_URL = "sqlite:////app/applications.db"
else:
    DATABASE_URL = "sqlite:///./applications.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

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