from typing import Any, Dict

from fastapi import Depends, HTTPException, Request

from app.core.persistence import SESSION_COOKIE_NAME, get_user_by_session_token


def get_current_user(request: Request) -> Dict[str, Any] | None:
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    return get_user_by_session_token(token)


def require_current_user(user: Dict[str, Any] | None = Depends(get_current_user)) -> Dict[str, Any]:
    if user is None:
        raise HTTPException(status_code=401, detail="请先登录。")
    return user
