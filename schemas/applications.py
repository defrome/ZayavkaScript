from pydantic import BaseModel
from typing import Union

class ApplicationUserData(BaseModel):
    name: str
    telephone_number: Union[str]
    time_slot: Union[str]