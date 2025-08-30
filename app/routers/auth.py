from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db import crud
from app.core.auth import get_password_hash

router = APIRouter(prefix="", tags=["auth"])  # keep /register at root
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "register.html", {"request": request, "error": None}
    )


@router.post("/register")
async def register_submit(
    request: Request,
    email: str = Form(...),
    full_name: str | None = Form(None),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> Response:
    email = email.strip().lower()
    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Password must be at least 8 characters."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    existing = await crud.get_user_by_email(db, email)
    if existing is not None:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    hashed = get_password_hash(password)
    await crud.create_user(db, email=email, full_name=full_name, hashed_password=hashed)

    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
