from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

router = APIRouter(tags=["admin-panel"])
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def user_panel() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "user.html")


@router.get("/admin", response_class=HTMLResponse, include_in_schema=False)
def admin_panel() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "admin.html")
