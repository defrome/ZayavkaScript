from pydantic import BaseModel

class MasterTimeResponse(BaseModel):
    id: int
    time_slot: str

    class Config:
        from_attributes = True

class MasterResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True