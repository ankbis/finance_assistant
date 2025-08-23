from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.api.router.items import router as items_router
from app.router import pages, admin

# Optional: feature flag for docs in prod (fallbacks if not defined in settings)
_DOCS_URL = "/docs" if getattr(settings, "ENABLE_DOCS", True) else None
_REDOC_URL = "/redoc" if getattr(settings, "ENABLE_REDOC", True) else None

app = FastAPI(
    title=getattr(settings, "APP_NAME", "App"),
    docs_url=_DOCS_URL,
    redoc_url=_REDOC_URL,
)

# Static files (expects ./static directory at project root)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Sessions for login + toasts (requires SECRET_KEY)
SECRET_KEY = getattr(settings, "SECRET_KEY", "change-me")
SESSION_COOKIE_NAME = getattr(settings, "SESSION_COOKIE_NAME", "fa_session")
ENV = getattr(settings, "ENV", "dev")

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie=SESSION_COOKIE_NAME,
    same_site="lax",
    https_only=False if ENV == "dev" else True,
)

# Store env name for templates
app.state.env_name = ENV

# ---- Your existing routes ----
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", include_in_schema=False)
def root():
    return {
        "message": f"{getattr(settings, 'APP_NAME', 'App')} is running",
        "docs": _DOCS_URL,
        "health": "/health",
    }

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return RedirectResponse(url="https://fastapi.tiangolo.com/img/favicon.png")

app.include_router(items_router)
app.include_router(pages.router)
app.include_router(admin.router)
