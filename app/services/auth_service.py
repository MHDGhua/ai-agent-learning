from typing import Any, Dict, Tuple

from app.core.persistence import (
    authenticate_user,
    change_user_password,
    create_session,
    create_user,
    delete_session,
    record_activity,
    update_user_profile,
)


def register_user(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    user = create_user(
        email=payload["email"],
        password=payload["password"],
        full_name=payload["full_name"],
        role=payload.get("role", "案件申请人"),
    )
    token = create_session(user["id"])
    record_activity(user["id"], "账户已创建", f"{user['full_name']} 已注册并登录。")
    return user, token


def login_user(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], str] | Tuple[None, None]:
    user = authenticate_user(email=payload["email"], password=payload["password"])
    if user is None:
        return None, None
    token = create_session(user["id"])
    record_activity(user["id"], "登录成功", f"{user['full_name']} 已进入工作台。")
    return user, token


def logout_user(token: str, user: Dict[str, Any] | None) -> None:
    if token:
        delete_session(token)
    if user is not None:
        record_activity(user["id"], "已退出登录", f"{user['full_name']} 已退出当前会话。")


def update_profile(user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    user = update_user_profile(
        user_id=user_id,
        full_name=payload["full_name"],
        role=payload.get("role", "案件申请人"),
    )
    record_activity(user_id, "资料已更新", "账户姓名或身份标签已更新。")
    return user


def update_password(user_id: int, current_password: str, new_password: str) -> Tuple[Dict[str, Any], str]:
    user = change_user_password(
        user_id=user_id,
        current_password=current_password,
        new_password=new_password,
    )
    token = create_session(user["id"])
    record_activity(user["id"], "密码已修改", "账户密码已更新，旧会话已失效。")
    return user, token
