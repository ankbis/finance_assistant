from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth
from app.core.auth import verify_password
from app.db.session import get_db
from app.db import crud
from app.services.api_client import api_client, QueryRequest

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _flash(request: Request, message: str, kind: str = "ok") -> None:
    toasts = request.session.get("toasts", [])
    toasts.append({"message": message, "kind": kind})
    request.session["toasts"] = toasts


def _pop_toasts(request: Request) -> list[dict]:
    return request.session.pop("toasts", [])


def _ctx(request: Request) -> dict:
    return {
        "request": request,
        "path": request.url.path,
        "user": request.session.get("user"),
        "env": request.app.state.env_name,
        "toasts": _pop_toasts(request),
    }


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", _ctx(request))


@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", _ctx(request))

@router.get("/admin")
async def login_form(request: Request):
    return templates.TemplateResponse("admin.html", _ctx(request))


@router.post("/login")
async def login(
    request: Request,
    email: str | None = Form(None),
    username: str | None = Form(
        None
    ),  # legacy support if template still posts 'username'
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    # Prefer email, fallback to username
    identifier = (email or username or "").strip().lower()
    if not identifier:
        _flash(request, "Email required", "err")
        return RedirectResponse(url="/login", status_code=303)

    # Look up user by email and verify password
    user = await crud.get_user_by_email(db, identifier)
    if user and verify_password(password, str(user.hashed_password)):
        # Store minimal identity (email or user.id) in session
        auth.login_user(request, user.email)
        _flash(request, "Signed in")
        return RedirectResponse(url="/", status_code=303)

    _flash(request, "Invalid credentials", "err")
    return RedirectResponse(url="/login", status_code=303)


@router.post("/logout")
async def logout(request: Request):
    auth.logout_user(request)
    _flash(request, "Signed out")
    return RedirectResponse(url="/", status_code=303)


@router.get("/queries")
async def queries_form(request: Request):
    ctx = _ctx(request)
    ctx["results"] = None
    return templates.TemplateResponse("queries.html", ctx)


@router.post("/queries")
async def run_query(request: Request, question: str = Form(...)):
    payload = QueryRequest(question=question)
    try:
        result = await api_client.run_query(payload)
        ctx = _ctx(request)
        ctx["results"] = result.model_dump()
        return templates.TemplateResponse("queries.html", ctx)
    except Exception as e:
        _flash(request, f"Query failed: {e}", "err")
        return RedirectResponse(url="/queries", status_code=303)
