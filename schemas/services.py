from typing import List

from pydantic import BaseModel

class TimeResponse(BaseModel):
    time_slot: str

    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    name: str
    description: str
    price: int