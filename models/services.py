from sqlalchemy import Column, Integer, String
from database.db import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String(100))
    price = Column(Integer)
    photo_url = Column(String)


