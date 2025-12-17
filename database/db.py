from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine("sqlite:///applications.db", echo=True)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

class Base(DeclarativeBase): pass