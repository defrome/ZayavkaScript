from pydantic import BaseModel
from typing import Union, Optional


class ApplicationCreate(BaseModel):
    service: str
    price: int
    date: Optional[str] = None
    user_name: str
    telephone_number: str
    time_slot: str
    master_name: str