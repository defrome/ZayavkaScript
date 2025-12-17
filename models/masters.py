from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from database.db import Base

master_time_association = Table(
    'master_time_association',
    Base.metadata,
    Column('master_id', Integer, ForeignKey('masters.id'), primary_key=True),
    Column('time_id', Integer, ForeignKey('master_times.id'), primary_key=True)
)


class Master(Base):
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    times = relationship("MasterTime",
                         secondary=master_time_association,
                         back_populates="masters")

    applications = relationship("Application", back_populates="master")


class MasterTime(Base):
    __tablename__ = "master_times"

    id = Column(Integer, primary_key=True)
    time_slot = Column(String)

    masters = relationship("Master",
                           secondary=master_time_association,
                           back_populates="times")

    applications = relationship("Application", back_populates="time_slot_obj")