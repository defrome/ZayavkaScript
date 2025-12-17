from typing import Optional

from pydantic import BaseModel

class MasterResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class MasterTimeCreate(BaseModel):
    time_slot: str

class MasterTimeResponse(BaseModel):
    id: int
    time_slot: str

    class Config:
        from_attributes = True