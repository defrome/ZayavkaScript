from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    telephone_number = Column(String(30))

    applications = relationship("Application", back_populates="user")