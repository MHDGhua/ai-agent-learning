from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.persistence import SESSION_COOKIE_NAME, SESSION_COOKIE_SECURE, SESSION_TTL_DAYS
from app.api.dependencies import get_current_user, require_current_user
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    PasswordChangeRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    SessionResponse,
    UserResponse,
)
from app.services.auth_service import login_user, logout_user, register_user, update_password, update_profile


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
        user, token = register_user(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    _set_session_cookie(response, token)
    return AuthResponse(user=UserResponse(**user))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, response: Response):
    user, token = login_user(request.model_dump())
    if user is None:
        raise HTTPException(status_code=401, detail="邮箱或密码错误。")
    _set_session_cookie(response, token)
    return AuthResponse(user=UserResponse(**user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response, user=Depends(get_current_user)):  # type: ignore[no-untyped-def]
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    logout_user(token, user)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return None


@router.get("/me", response_model=AuthResponse)
async def me(user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    return AuthResponse(user=UserResponse(**user))


@router.get("/session", response_model=SessionResponse)
async def session(user=Depends(get_current_user)):  # type: ignore[no-untyped-def]
    if user is None:
        return SessionResponse(user=None)
    return SessionResponse(user=UserResponse(**user))


@router.put("/profile", response_model=AuthResponse)
async def update_my_profile(
    request: ProfileUpdateRequest,
    user=Depends(require_current_user),  # type: ignore[no-untyped-def]
):
    try:
        updated_user = update_profile(user["id"], request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AuthResponse(user=UserResponse(**updated_user))


@router.post("/change-password", response_model=AuthResponse)
async def change_password(
    request: PasswordChangeRequest,
    response: Response,
    user=Depends(require_current_user),  # type: ignore[no-untyped-def]
):
    try:
        updated_user, token = update_password(
            user["id"],
            request.current_password,
            request.new_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _set_session_cookie(response, token)
    return AuthResponse(user=UserResponse(**updated_user))
