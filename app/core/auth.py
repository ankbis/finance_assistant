from fastapi import Request, HTTPException, status

def login_user(request: Request, username: str) -> None:
    request.session["user"] = {"username": username}

def logout_user(request: Request) -> None:
    request.session.pop("user", None)

def current_user(request: Request) -> dict | None:
    return request.session.get("user")

def require_user(request: Request) -> dict:
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, detail="login_required")
    return user
