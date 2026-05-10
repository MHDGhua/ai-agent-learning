from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.persistence import (
    SESSION_COOKIE_NAME,
    SESSION_COOKIE_SECURE,
    SESSION_TTL_DAYS,
    authenticate_user,
    create_session,
    create_user,
    delete_session,
    record_activity,
)
from app.api.dependencies import get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=SESSION_COOKIE_SECURE,
        path="/",
        max_age=SESSION_TTL_DAYS * 24 * 60 * 60,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, response: Response):
    try:
        user = create_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    token = create_session(user["id"])
    _set_session_cookie(response, token)
    record_activity(user["id"], "账户已创建", f"{user['full_name']} 已注册并登录。")
    return AuthResponse(user=UserResponse(**user))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, response: Response):
    user = authenticate_user(email=request.email, password=request.password)
    if user is None:
        raise HTTPException(status_code=401, detail="邮箱或密码错误。")
    token = create_session(user["id"])
    _set_session_cookie(response, token)
    record_activity(user["id"], "登录成功", f"{user['full_name']} 已进入工作台。")
    return AuthResponse(user=UserResponse(**user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response, user=Depends(get_current_user)):  # type: ignore[no-untyped-def]
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    if token:
        delete_session(token)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    if user is not None:
        record_activity(user["id"], "已退出登录", f"{user['full_name']} 已退出当前会话。")
    return None


@router.get("/me", response_model=AuthResponse)
async def me(user=Depends(get_current_user)):  # type: ignore[no-untyped-def]
    if user is None:
        raise HTTPException(status_code=401, detail="未登录。")
    return AuthResponse(user=UserResponse(**user))
