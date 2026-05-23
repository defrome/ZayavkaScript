from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from models.application import ApplicationSource, ApplicationStatus


class ApplicationCreatePublic(BaseModel):
    service_id: int
    name: str = Field(min_length=2, max_length=120)
    telephone_number: str = Field(min_length=5, max_length=30)
    appointment_date: date
    time_slot: str = Field(pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    comment: str | None = Field(default=None, max_length=500)


class ApplicationCreateAdmin(ApplicationCreatePublic):
    master_id: int


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationRead(BaseModel):
    id: int
    service_id: int
    service_name: str
    user_id: int
    customer_name: str
    customer_phone: str
    master_id: int | None
    master_name: str | None
    appointment_date: date
    time_slot: str
    status: ApplicationStatus
    source: ApplicationSource
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationListResponse(BaseModel):
    status: str
    data: list[ApplicationRead]
    source: str


class ApplicationCreateResponse(BaseModel):
    status: str
    data: ApplicationRead


class ApplicationStatusResponse(BaseModel):
    status: str
    data: ApplicationRead
