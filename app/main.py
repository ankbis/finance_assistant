from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.db.session import engine
from app.routers import pages, admin, auth, holdings

_DOCS_URL = "/docs" if getattr(settings, "ENABLE_DOCS", True) else None
_REDOC_URL = "/redoc" if getattr(settings, "ENABLE_REDOC", True) else None


# Lifespan: dispose the SQLAlchemy engine on shutdown to avoid lingering conns
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title=getattr(settings, "APP_NAME", "App"),
    docs_url=_DOCS_URL,
    redoc_url=_REDOC_URL,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

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

app.state.env_name = ENV


@app.get("/health")
def health():
    return {"status": "ok"}

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(pages.router)
app.include_router(holdings.router)

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


app.include_router(pages.router)
app.include_router(admin.router)
app.include_router(auth.router)
