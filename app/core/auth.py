from typing import Optional
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


SESSION_KEY = "user"


def login_user(request: Request, email: str) -> None:
    """Persist minimal user identity in the session."""
    request.session[SESSION_KEY] = {"email": email}


def logout_user(request: Request) -> None:
    """Clear the session identity."""
    request.session.pop(SESSION_KEY, None)


def get_current_user(request: Request) -> Optional[dict]:
    """Return the session user payload or None."""
    return request.session.get(SESSION_KEY)


def is_authenticated(request: Request) -> bool:
    return get_current_user(request) is not None


def require_user_or_redirect(
    request: Request, next_url: Optional[str] = None
) -> Optional[Response]:
    """
    Convenience helper for page handlers.
    If not logged in, returns a RedirectResponse to /login (with ?next=...).
    Otherwise returns None (caller should continue).
    """
    if is_authenticated(request):
        return None
    target = "/login"
    if next_url:
        target = f"{target}?next={next_url}"
    else:
        try:
            target = f"{target}?next={request.url.path}"
        except Exception:
            pass
    return RedirectResponse(url=target, status_code=303)
