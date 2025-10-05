from fastapi import Request
from app.core.auth import get_current_user
from app.db.crud.users import get_user_by_email
from sqlalchemy.ext.asyncio import AsyncSession


def get_flash_messages(request: Request) -> list[dict]:
    """Get and clear flash messages from session."""
    return request.session.pop("flash_messages", [])


def add_flash_message(request: Request, message: str, kind: str = "info") -> None:
    """Add a flash message to session."""
    messages = request.session.get("flash_messages", [])
    messages.append({"message": message, "kind": kind})
    request.session["flash_messages"] = messages


async def get_template_context(request: Request, db: AsyncSession | None = None) -> dict:
    """Get common template context including user info."""
    current_user = get_current_user(request)
    context = {
        "request": request,
        "path": request.url.path,
        "user": current_user,
        "user_display": None,
        "flash_messages": get_flash_messages(request)
    }
    
    if current_user and db:
        user = await get_user_by_email(db, current_user["email"])
        if user:
            context["user_display"] = user.full_name or user.email
            
    return context