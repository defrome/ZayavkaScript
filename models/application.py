from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)

    price = Column(Integer, ForeignKey("services.price"))
    service = Column(String, ForeignKey("services.id"))
    user_id = Column(Integer, ForeignKey('users.id'))
    master_id = Column(Integer, ForeignKey('masters.id'))
    time_id = Column(Integer, ForeignKey('master_times.id'))

    user = relationship("User", back_populates="applications")
    master = relationship("Master", back_populates="applications")
    time_slot_obj = relationship("MasterTime", back_populates="applications")