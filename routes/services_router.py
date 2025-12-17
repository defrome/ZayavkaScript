from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import db
from database.db import get_db
from schemas.services import ServiceCreate
from services.services import ServicesService

router = APIRouter()

@router.post("/services")
def create_services(serviceCreate: ServiceCreate,
                    db: Session = Depends(get_db)):

    service_services = ServicesService(db)

    result = service_services.create_services(
        name=serviceCreate.name,
        description=serviceCreate.description,
        price=serviceCreate.price
    )

    return {"status": "success",
            "data": result}