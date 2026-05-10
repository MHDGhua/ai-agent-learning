import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config.settings import DATABASE_URL


PASSWORD_HASH_ITERATIONS = int(os.getenv("PASSWORD_HASH_ITERATIONS", "240000"))
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "lerap_session")
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
SESSION_TTL_DAYS = int(os.getenv("SESSION_TTL_DAYS", "7"))

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_sqlite_path(database_url: str) -> Path:
    raw = (database_url or "").strip()
    if not raw.startswith("sqlite:///"):
        raise RuntimeError("当前持久化层只支持 sqlite:/// 数据库 URL。")
    target = raw.replace("sqlite:///", "", 1)
    path = Path(target)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


DB_PATH = _resolve_sqlite_path(DATABASE_URL)


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def ensure_database() -> None:
    with _get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT '案件申请人',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS saved_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                case_type TEXT NOT NULL DEFAULT '',
                primary_finding TEXT NOT NULL DEFAULT '',
                readiness TEXT NOT NULL DEFAULT '',
                next_best_action TEXT NOT NULL DEFAULT '',
                snapshot_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                case_id INTEGER,
                title TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (case_id) REFERENCES saved_cases(id) ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_saved_cases_user_id ON saved_cases(user_id, updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id, created_at DESC);
            """
        )


def _row_to_user(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    return {
        "id": row["id"],
        "email": row["email"],
        "full_name": row["full_name"],
        "role": row["role"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        PASSWORD_HASH_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt}${digest}"


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, rounds, salt, digest = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        int(rounds),
    ).hex()
    return secrets.compare_digest(candidate, digest)


def _hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def create_user(*, email: str, password: str, full_name: str, role: str) -> Dict[str, Any]:
    now = _utc_now()
    normalized_email = _normalize_email(email)
    with _get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE lower(email) = lower(?)",
            (normalized_email,),
        ).fetchone()
        if existing is not None:
            raise ValueError("该邮箱已注册。")
        cursor = connection.execute(
            """
            INSERT INTO users (email, password_hash, full_name, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                normalized_email,
                _hash_password(password),
                full_name.strip(),
                role.strip() or "案件申请人",
                now,
                now,
            ),
        )
        row = connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return _row_to_user(row) or {}


def authenticate_user(*, email: str, password: str) -> Optional[Dict[str, Any]]:
    normalized_email = _normalize_email(email)
    with _get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE lower(email) = lower(?)",
            (normalized_email,),
        ).fetchone()
    if row is None or not _verify_password(password, row["password_hash"]):
        return None
    return _row_to_user(row)


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return _row_to_user(row)


def update_user_profile(*, user_id: int, full_name: str, role: str) -> Dict[str, Any]:
    now = _utc_now()
    with _get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if existing is None:
            raise ValueError("用户不存在。")
        connection.execute(
            "UPDATE users SET full_name = ?, role = ?, updated_at = ? WHERE id = ?",
            (full_name.strip(), role.strip() or "案件申请人", now, user_id),
        )
        updated = connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return _row_to_user(updated) or {}


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=SESSION_TTL_DAYS)
    with _get_connection() as connection:
        connection.execute(
            """
            INSERT INTO sessions (user_id, session_token_hash, expires_at, created_at, last_seen_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                _hash_session_token(token),
                expires_at.isoformat(),
                now.isoformat(),
                now.isoformat(),
            ),
        )
    return token


def delete_session(token: str) -> None:
    if not token:
        return
    token_hash = _hash_session_token(token)
    with _get_connection() as connection:
        connection.execute(
            "DELETE FROM sessions WHERE session_token_hash = ?",
            (token_hash,),
        )


def delete_user_sessions(user_id: int) -> None:
    with _get_connection() as connection:
        connection.execute(
            "DELETE FROM sessions WHERE user_id = ?",
            (user_id,),
        )


def cleanup_expired_sessions() -> None:
    with _get_connection() as connection:
        connection.execute(
            "DELETE FROM sessions WHERE expires_at < ?",
            (_utc_now(),),
        )


def get_user_by_session_token(token: str) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    cleanup_expired_sessions()
    now = _utc_now()
    token_hash = _hash_session_token(token)
    with _get_connection() as connection:
        row = connection.execute(
            """
            SELECT users.*
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.session_token_hash = ? AND sessions.expires_at >= ?
            """,
            (token_hash, now),
        ).fetchone()
        if row is not None:
            connection.execute(
                "UPDATE sessions SET last_seen_at = ? WHERE session_token_hash = ?",
                (now, token_hash),
            )
    return _row_to_user(row)


def change_user_password(*, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
    now = _utc_now()
    with _get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            raise ValueError("用户不存在。")
        if not _verify_password(current_password, row["password_hash"]):
            raise ValueError("当前密码错误。")
        if _verify_password(new_password, row["password_hash"]):
            raise ValueError("新密码不能与当前密码相同。")
        connection.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
            (_hash_password(new_password), now, user_id),
        )
        connection.execute(
            "DELETE FROM sessions WHERE user_id = ?",
            (user_id,),
        )
        updated = connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return _row_to_user(updated) or {}


def build_case_title(snapshot: Dict[str, Any], case_type: str) -> str:
    title = str(snapshot.get("title") or "").strip()
    if title:
        return title
    case_form = snapshot.get("caseForm") or {}
    applicant_info = case_form.get("applicant_info") or {}
    employer = str(applicant_info.get("employer_name") or "").strip()
    if employer and case_type:
        return f"{case_type} · {employer}"
    if employer:
        return employer
    return case_type or "未命名案件"


def _summary_from_case_row(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "case_type": row["case_type"],
        "primary_finding": row["primary_finding"],
        "readiness": row["readiness"],
        "next_best_action": row["next_best_action"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def save_case(user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    snapshot = payload.get("snapshot") or {}
    case_id = payload.get("id")
    case_type = str(payload.get("case_type") or snapshot.get("caseType") or "").strip()
    title = build_case_title(snapshot, case_type)
    primary_finding = str(payload.get("primary_finding") or "").strip()
    readiness = str(payload.get("readiness") or "").strip()
    next_best_action = str(payload.get("next_best_action") or "").strip()
    serialized_snapshot = json.dumps(snapshot, ensure_ascii=False)
    now = _utc_now()

    with _get_connection() as connection:
        if case_id:
            existing = connection.execute(
                "SELECT id FROM saved_cases WHERE id = ? AND user_id = ?",
                (case_id, user_id),
            ).fetchone()
            if existing is None:
                raise ValueError("案件不存在或无权访问。")
            connection.execute(
                """
                UPDATE saved_cases
                SET title = ?, case_type = ?, primary_finding = ?, readiness = ?,
                    next_best_action = ?, snapshot_json = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (
                    title,
                    case_type,
                    primary_finding,
                    readiness,
                    next_best_action,
                    serialized_snapshot,
                    now,
                    case_id,
                    user_id,
                ),
            )
            final_id = int(case_id)
        else:
            cursor = connection.execute(
                """
                INSERT INTO saved_cases (
                    user_id, title, case_type, primary_finding, readiness,
                    next_best_action, snapshot_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    title,
                    case_type,
                    primary_finding,
                    readiness,
                    next_best_action,
                    serialized_snapshot,
                    now,
                    now,
                ),
            )
            final_id = int(cursor.lastrowid)

        row = connection.execute(
            "SELECT * FROM saved_cases WHERE id = ? AND user_id = ?",
            (final_id, user_id),
        ).fetchone()
    return get_case(user_id, final_id) if row is not None else {}


def get_case(user_id: int, case_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM saved_cases WHERE id = ? AND user_id = ?",
            (case_id, user_id),
        ).fetchone()
    if row is None:
        return None
    summary = _summary_from_case_row(row)
    summary["snapshot"] = json.loads(row["snapshot_json"])
    return summary


def list_cases(user_id: int) -> List[Dict[str, Any]]:
    with _get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM saved_cases WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
    return [_summary_from_case_row(row) for row in rows]


def delete_case(user_id: int, case_id: int) -> bool:
    with _get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM saved_cases WHERE id = ? AND user_id = ?",
            (case_id, user_id),
        )
    return cursor.rowcount > 0


def record_activity(user_id: int, title: str, detail: str, case_id: Optional[int] = None) -> Dict[str, Any]:
    now = _utc_now()
    with _get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO activities (user_id, case_id, title, detail, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, case_id, title.strip(), detail.strip(), now),
        )
        row = connection.execute(
            "SELECT * FROM activities WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return {
        "id": row["id"],
        "title": row["title"],
        "detail": row["detail"],
        "created_at": row["created_at"],
        "case_id": row["case_id"],
    }


def list_activities(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    with _get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM activities
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "detail": row["detail"],
            "created_at": row["created_at"],
            "case_id": row["case_id"],
        }
        for row in rows
    ]
