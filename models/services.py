from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.db import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String(100))
    price = Column(Integer)


