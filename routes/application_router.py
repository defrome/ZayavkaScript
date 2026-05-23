from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from database.db import get_db
from database.redis_client import delete_cache, get_cache, set_cache
from schemas.applications import ApplicationCreatePublic
from services.applications import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/get_applications")
def get_all_applications(db: Session = Depends(get_db)):
    cache_key = "all_applications"

    cached_data = get_cache(cache_key)
    if cached_data:
        return {"status": "success", "data": cached_data, "source": "cache"}

    app_service = ApplicationService(db)
    result = app_service.list_applications(only_active=False)

    result_json = jsonable_encoder(result)
    set_cache(cache_key, result_json)

    return {"status": "success", "data": result, "source": "db"}

@router.post("/create_application", status_code=status.HTTP_201_CREATED)
def create_application(
        application_data: ApplicationCreatePublic,
        db: Session = Depends(get_db)
):
    try:
        app_service = ApplicationService(db)
        result = app_service.create_public_application(
            service_id=application_data.service_id,
            name=application_data.name,
            telephone_number=application_data.telephone_number,
            appointment_date=application_data.appointment_date,
            time_slot=application_data.time_slot,
            comment=application_data.comment,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании заявки: {exc}",
        ) from exc

    delete_cache("all_masters")
    delete_cache("all_applications")

    return {"status": "success", "data": result}
