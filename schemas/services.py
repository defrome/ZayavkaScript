from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: int = Field(ge=0)
    photo_url: str | None = Field(default=None, max_length=500)


class ServiceRead(BaseModel):
    id: int
    name: str
    description: str | None
    price: int
    photo_url: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceListResponse(BaseModel):
    status: str
    data: list[ServiceRead]
    source: str
