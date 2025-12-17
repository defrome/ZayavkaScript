from fastapi import APIRouter

router = APIRouter()

@router.post("/services")
def create_services():
    return {"service": "services"}