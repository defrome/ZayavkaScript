from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, selectinload

from database.db import get_db
from database.redis_client import delete_cache_by_pattern, get_cache, set_cache
from models.masters import Master, MasterTime
from schemas.applications import ApplicationCreatePublic, ApplicationCreateResponse, ApplicationListResponse
from schemas.masters import MasterListResponse
from schemas.services import ServiceListResponse
from services.applications import ApplicationService
from services.masters import MasterService
from services.services import ServicesService

router = APIRouter(prefix="/api/v1/public", tags=["public"])


@router.get("/services", response_model=ServiceListResponse)
def list_services(db: Session = Depends(get_db)):
    cache_key = "public:services:active"
    cached = get_cache(cache_key)
    if cached is not None:
        return {"status": "success", "data": cached, "source": "cache"}

    service_service = ServicesService(db)
    services = service_service.list_services(active_only=True)
    payload = [
        {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "price": service.price,
            "photo_url": service.photo_url,
            "is_active": service.is_active,
            "created_at": service.created_at,
        }
        for service in services
    ]
    set_cache(cache_key, payload)
    return {"status": "success", "data": payload, "source": "db"}


@router.get("/masters", response_model=MasterListResponse)
def list_masters(
    day: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    cache_key = f"public:masters:day:{day.isoformat() if day else 'all'}"
    cached = get_cache(cache_key)
    if cached is not None:
        return {"status": "success", "data": cached, "source": "cache"}

    master_service = MasterService(db)
    masters = master_service.list_masters(active_only=True)

    payload = []
    for master in masters:
        if day:
            filtered_times = [slot for slot in master.times if slot.day == day and slot.is_available]
        else:
            filtered_times = [slot for slot in master.times if slot.is_available]

        payload.append(
            {
                "id": master.id,
                "name": master.name,
                "is_active": master.is_active,
                "times": [
                    {
                        "id": slot.id,
                        "day": slot.day,
                        "time_slot": slot.time_slot,
                        "is_available": slot.is_available,
                    }
                    for slot in sorted(filtered_times, key=lambda s: (s.day, s.time_slot))
                ],
            }
        )

    set_cache(cache_key, payload)
    return {"status": "success", "data": payload, "source": "db"}


@router.post("/applications", response_model=ApplicationCreateResponse)
def create_public_application(payload: ApplicationCreatePublic, db: Session = Depends(get_db)):
    app_service = ApplicationService(db)
    created = app_service.create_public_application(
        service_id=payload.service_id,
        name=payload.name,
        telephone_number=payload.telephone_number,
        appointment_date=payload.appointment_date,
        time_slot=payload.time_slot,
        comment=payload.comment,
    )

    delete_cache_by_pattern("admin:applications:*")
    delete_cache_by_pattern("public:masters:*")

    return {"status": "success", "data": created}
