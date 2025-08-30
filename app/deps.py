from fastapi import Request
from app.core.auth import current_user


def template_ctx(request: Request) -> dict:
    return {
        "user": current_user(request),
        "path": request.url.path,
        "env": request.app.state.env_name,
    }
