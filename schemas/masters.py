from pydantic import BaseModel

class MasterResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True