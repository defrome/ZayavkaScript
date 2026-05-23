from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class MasterCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class MasterTimeCreate(BaseModel):
    day: date
    time_slot: str = Field(pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")


class MasterTimeRead(BaseModel):
    id: int
    day: date
    time_slot: str
    is_available: bool

    model_config = ConfigDict(from_attributes=True)


class MasterRead(BaseModel):
    id: int
    name: str
    is_active: bool
    times: list[MasterTimeRead]

    model_config = ConfigDict(from_attributes=True)


class MasterListResponse(BaseModel):
    status: str
    data: list[MasterRead]
    source: str
