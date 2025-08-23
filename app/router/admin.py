from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.core import auth

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

@router.get("/admin")
async def admin_page(request: Request):
    auth.require_user(request)
    ctx = _ctx(request)
    ctx["flags"] = {"disable_docs": False}
    return templates.TemplateResponse("admin.html", ctx)

@router.post("/admin/seed")
async def run_seed(request: Request):
    auth.require_user(request)
    # TODO: call your real seed logic here
    _flash(request, "Seed completed")
    return RedirectResponse(url="/admin", status_code=303)
