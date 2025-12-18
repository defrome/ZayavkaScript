from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from database.redis_client import delete_cache, set_cache, get_cache
from schemas.services import ServiceCreate
from services.services import ServicesService

router = APIRouter()


@router.get("/services")
def get_services(db: Session = Depends(get_db)):
    cached_services = get_cache("all_services")
    if cached_services:
        return {"status": "success", "data": cached_services, "source": "cache"}

    service_services = ServicesService(db)
    result = service_services.get_all_services()

    set_cache("all_services", result)

    return {"status": "success", "data": result, "source": "db"}


@router.post("/services")
def create_services(serviceCreate: ServiceCreate, db: Session = Depends(get_db)):
    service_services = ServicesService(db)

    result = service_services.create_services(
        name=serviceCreate.name,
        description=serviceCreate.description,
        price=serviceCreate.price,
        photo_url=serviceCreate.photo_url,
    )

    delete_cache("all_services")

    return {"status": "success", "data": result}