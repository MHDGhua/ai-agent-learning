from datetime import datetime, timedelta, timezone
from typing import Any, Dict, TypedDict

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
from app.schemas.workspace import ActivityListResponse
from app.services.auth_service import login_user, logout_user, register_user, update_password, update_profile
from app.services.workspace_service import list_workspace_activities


router = APIRouter(prefix="/auth", tags=["auth"])

MAX_LOGIN_FAILURES = 5
LOGIN_FAILURE_WINDOW = timedelta(minutes=15)


class LoginFailureState(TypedDict):
    count: int
    first_failed_at: datetime


_login_failures: Dict[str, LoginFailureState] = {}


def _login_failure_key(request: Request, email: str) -> str:
    client_host = request.client.host if request.client else "unknown"
    return f"{email.strip().lower()}:{client_host}"


def _get_active_failure_state(key: str) -> LoginFailureState | None:
    state = _login_failures.get(key)
    if state is None:
        return None
    if datetime.now(timezone.utc) - state["first_failed_at"] > LOGIN_FAILURE_WINDOW:
        _login_failures.pop(key, None)
        return None
    return state


def _is_login_limited(key: str) -> bool:
    state = _get_active_failure_state(key)
    return bool(state and state["count"] >= MAX_LOGIN_FAILURES)


def _record_login_failure(key: str) -> None:
    state = _get_active_failure_state(key)
    if state is None:
        _login_failures[key] = {"count": 1, "first_failed_at": datetime.now(timezone.utc)}
        return
    state["count"] += 1


def _clear_login_failures(key: str) -> None:
    _login_failures.pop(key, None)


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
async def register(request: RegisterRequest, response: Response) -> AuthResponse:
    try:
        user, token = register_user(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    _set_session_cookie(response, token)
    return AuthResponse(user=UserResponse(**user))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, response: Response, http_request: Request) -> AuthResponse:
    failure_key = _login_failure_key(http_request, request.email)
    if _is_login_limited(failure_key):
        raise HTTPException(status_code=429, detail="登录失败次数过多，请 15 分钟后再试。")

    user, token = login_user(request.model_dump())
    if user is None:
        _record_login_failure(failure_key)
        if _is_login_limited(failure_key):
            raise HTTPException(status_code=429, detail="登录失败次数过多，请 15 分钟后再试。")
        raise HTTPException(status_code=401, detail="邮箱或密码错误。")

    _clear_login_failures(failure_key)
    _set_session_cookie(response, token)
    return AuthResponse(user=UserResponse(**user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    user: Dict[str, Any] | None = Depends(get_current_user),
) -> None:
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    logout_user(token, user)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return None


@router.get("/me", response_model=AuthResponse)
async def me(user: Dict[str, Any] = Depends(require_current_user)) -> AuthResponse:
    return AuthResponse(user=UserResponse(**user))


@router.get("/session", response_model=SessionResponse)
async def session(user: Dict[str, Any] | None = Depends(get_current_user)) -> SessionResponse:
    if user is None:
        return SessionResponse(user=None)
    return SessionResponse(user=UserResponse(**user))


@router.get("/activity", response_model=ActivityListResponse)
async def activity(user: Dict[str, Any] = Depends(require_current_user)) -> ActivityListResponse:
    return ActivityListResponse(items=list_workspace_activities(user["id"], limit=20))


@router.put("/profile", response_model=AuthResponse)
async def update_my_profile(
    request: ProfileUpdateRequest,
    user: Dict[str, Any] = Depends(require_current_user),
) -> AuthResponse:
    try:
        updated_user = update_profile(user["id"], request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AuthResponse(user=UserResponse(**updated_user))


@router.post("/change-password", response_model=AuthResponse)
async def change_password(
    request: PasswordChangeRequest,
    response: Response,
    user: Dict[str, Any] = Depends(require_current_user),
) -> AuthResponse:
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
