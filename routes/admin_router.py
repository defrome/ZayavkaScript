from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.db import get_db
from database.redis_client import delete_cache_by_pattern, get_cache, set_cache
from models.application import ApplicationStatus
from routes.dependencies import require_admin_token
from schemas.applications import (
    ApplicationCreateAdmin,
    ApplicationCreateResponse,
    ApplicationListResponse,
    ApplicationStatusResponse,
    ApplicationStatusUpdate,
)
from schemas.masters import MasterCreate, MasterTimeCreate
from schemas.services import ServiceCreate
from services.applications import ApplicationService
from services.masters import MasterService
from services.services import ServicesService

router = APIRouter(prefix="/api/v1/admin", tags=["admin"], dependencies=[Depends(require_admin_token)])


@router.post("/services")
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    service_service = ServicesService(db)
    service = service_service.create_service(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        photo_url=payload.photo_url,
    )

    delete_cache_by_pattern("public:services:*")

    return {
        "status": "success",
        "data": {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "price": service.price,
            "photo_url": service.photo_url,
            "is_active": service.is_active,
            "created_at": service.created_at,
        },
    }


@router.post("/masters")
def create_master(payload: MasterCreate, db: Session = Depends(get_db)):
    master_service = MasterService(db)
    master = master_service.create_master(payload.name)
    delete_cache_by_pattern("public:masters:*")

    return {
        "status": "success",
        "data": {"id": master.id, "name": master.name, "is_active": master.is_active},
    }


@router.post("/masters/{master_id}/times")
def add_master_time(master_id: int, payload: MasterTimeCreate, db: Session = Depends(get_db)):
    master_service = MasterService(db)
    slot = master_service.add_time_to_master(master_id=master_id, day=payload.day, time_slot=payload.time_slot)

    delete_cache_by_pattern("public:masters:*")

    return {
        "status": "success",
        "data": {
            "id": slot.id,
            "master_id": slot.master_id,
            "day": slot.day,
            "time_slot": slot.time_slot,
            "is_available": slot.is_available,
        },
    }


@router.post("/applications", response_model=ApplicationCreateResponse)
def create_admin_application(payload: ApplicationCreateAdmin, db: Session = Depends(get_db)):
    app_service = ApplicationService(db)
    created = app_service.create_admin_application(
        service_id=payload.service_id,
        name=payload.name,
        telephone_number=payload.telephone_number,
        appointment_date=payload.appointment_date,
        time_slot=payload.time_slot,
        master_id=payload.master_id,
        comment=payload.comment,
    )

    delete_cache_by_pattern("admin:applications:*")
    delete_cache_by_pattern("public:masters:*")

    return {"status": "success", "data": created}


@router.get("/applications", response_model=ApplicationListResponse)
def list_applications(
    status: ApplicationStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    cache_key = f"admin:applications:status:{status.value if status else 'all'}"
    cached = get_cache(cache_key)
    if cached is not None:
        return {"status": "success", "data": cached, "source": "cache"}

    app_service = ApplicationService(db)
    data = app_service.list_applications(only_active=False, status_filter=status)
    set_cache(cache_key, data)
    return {"status": "success", "data": data, "source": "db"}


@router.get("/applications/actual", response_model=ApplicationListResponse)
def list_actual_applications(db: Session = Depends(get_db)):
    cache_key = "admin:applications:actual"
    cached = get_cache(cache_key)
    if cached is not None:
        return {"status": "success", "data": cached, "source": "cache"}

    app_service = ApplicationService(db)
    data = app_service.list_applications(only_active=True)
    set_cache(cache_key, data)
    return {"status": "success", "data": data, "source": "db"}


@router.patch("/applications/{application_id}/status", response_model=ApplicationStatusResponse)
def update_application_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
):
    app_service = ApplicationService(db)
    updated = app_service.update_status(application_id=application_id, new_status=payload.status)

    delete_cache_by_pattern("admin:applications:*")
    delete_cache_by_pattern("public:masters:*")

    return {"status": "success", "data": updated}
