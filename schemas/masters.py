from typing import List

from pydantic import BaseModel

class TimeResponse(BaseModel):
    time_slot: str

    class Config:
        from_attributes = True

class MasterResponse(BaseModel):
    id: int
    name: str
    times: List[TimeResponse] = []

    class Config:
        from_attributes = True

class MasterListEnvelope(BaseModel):
    status: str
    data: List[MasterResponse]
    source: str

class MasterTimeCreate(BaseModel):
    time_slot: str

    class Config:
        from_attributes = True