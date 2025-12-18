from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from models import Service
from schemas.applications import ApplicationCreate
from services.applications import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/create_application", status_code=status.HTTP_201_CREATED)
def create_application(
        application_data: ApplicationCreate,
        db: Session = Depends(get_db)
):
    db_service = db.query(Service).filter(Service.id == application_data.service_id).first()

    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Услуга с ID {application_data.service_id} не найдена"
        )

    app_service = ApplicationService(
        service=db_service.name,
        price=db_service.price,
        date=application_data.date
    )

    result = app_service.create_application(
        db=db,
        name=application_data.name,
        telephone_number=application_data.telephone_number,
        time_slot=application_data.time_slot,
        master_name=application_data.master_name
    )

    if result.get("success"):
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )