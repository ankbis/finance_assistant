from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth
from app.core.auth import verify_password, get_current_user
from app.core.context import get_template_context, add_flash_message
from app.db.session import get_db
from app.db import crud
from app.db.crud.users import get_user_by_email
from app.services.api_client import api_client, QueryRequest

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _flash(request: Request, message: str, kind: str = "ok") -> None:
    toasts = request.session.get("toasts", [])
    toasts.append({"message": message, "kind": kind})
    request.session["toasts"] = toasts


def _pop_toasts(request: Request) -> list[dict]:
    return request.session.pop("toasts", [])


def _display_name(u):
    if isinstance(u, dict):
        return u.get("full_name") or u.get("username") or u.get("email")
    return str(u) if u else None

@router.get("/")
async def home(
    request: Request,
    current_user: dict | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    context = await get_template_context(request, db)
    return templates.TemplateResponse("home.html", context)


@router.get("/login")
async def login_form(
    request: Request, 
    current_user: dict | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user:
        return RedirectResponse(url="/", status_code=303)
    context = await get_template_context(request, db)
    return templates.TemplateResponse("login.html", context)

@router.get("/admin")
async def admin(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    context = await get_template_context(request, db)
    return templates.TemplateResponse("admin.html", context)


@router.post("/query")
async def run_query(
    request: Request,
    query: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if not query:
        return RedirectResponse("/", status_code=303)

    context = await get_template_context(request, db)
    try:
        resp = await api_client.send_query(QueryRequest(query=query))
        context.update({
            "query": query,
            "result": resp.response,
            "error": None,
        })
    except Exception as e:
        context.update({
            "query": query,
            "result": None,
            "error": str(e),
        })

    return templates.TemplateResponse("queries.html", context)


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
    add_flash_message(request, "Signed out")
    return RedirectResponse(url="/", status_code=303)


@router.get("/queries")
async def queries_form(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    context = await get_template_context(request, db)
    context["results"] = None
    return templates.TemplateResponse("queries.html", context)


@router.post("/queries")
async def run_query(
    request: Request,
    question: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    payload = QueryRequest(question=question)
    try:
        result = await api_client.run_query(payload)
        context = await get_template_context(request, db)
        context["results"] = result.model_dump()
        return templates.TemplateResponse("queries.html", context)
    except Exception as e:
        add_flash_message(request, f"Query failed: {e}", "error")
        return RedirectResponse(url="/queries", status_code=303)
