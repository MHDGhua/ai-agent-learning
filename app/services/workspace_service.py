from typing import Any, Dict, List

from app.core.persistence import delete_case, get_case, list_activities, list_cases, record_activity, save_case


def list_workspace_cases(user_id: int) -> List[Dict[str, Any]]:
    return list_cases(user_id)


def get_workspace_case(user_id: int, case_id: int) -> Dict[str, Any] | None:
    return get_case(user_id, case_id)


def save_workspace_case(user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    saved = save_case(user_id, payload)
    record_activity(
        user_id,
        "案件已保存",
        f"{saved['title']} 已保存到服务端。",
        case_id=saved["id"],
    )
    return saved


def remove_workspace_case(user_id: int, case_id: int) -> bool:
    deleted = delete_case(user_id, case_id)
    if deleted:
        record_activity(user_id, "案件已删除", f"案件 #{case_id} 已从服务端移除。")
    return deleted


def list_workspace_activities(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    return list_activities(user_id, limit=limit)


def import_legacy_workspace(
    user_id: int,
    *,
    history_entries: List[Dict[str, Any]],
    activities: List[Dict[str, Any]],
) -> Dict[str, Any]:
    imported_case_ids: List[int] = []
    imported_activities = 0

    for entry in history_entries:
        snapshot = {
            "title": entry.get("title") or "未命名案件",
            "caseForm": entry.get("caseForm") or {},
            "evidenceText": entry.get("evidenceText") or "",
            "documentType": (entry.get("documentResult") or {}).get("document_type")
            or entry.get("documentType")
            or "仲裁申请书",
            "workupResult": entry.get("workupResult"),
            "documentResult": entry.get("documentResult"),
            "documentValidation": entry.get("documentValidation"),
            "legacyMessages": entry.get("messages") or [],
            "legacyUploadedFiles": entry.get("uploadedFiles") or [],
            "legacySource": "localStorage",
        }
        payload = {
            "title": entry.get("title") or "未命名案件",
            "case_type": ((entry.get("workupResult") or {}).get("analysis") or {}).get("case_type")
            or entry.get("kindLabel")
            or "",
            "primary_finding": entry.get("primaryFinding") or "",
            "readiness": entry.get("readiness") or "",
            "next_best_action": entry.get("nextBestAction") or "",
            "snapshot": snapshot,
        }
        saved = save_case(user_id, payload)
        imported_case_ids.append(saved["id"])

    for item in activities:
        title = str(item.get("title") or "历史动作").strip()
        detail = str(item.get("detail") or "来自旧版本地记录。").strip()
        record_activity(user_id, title, detail)
        imported_activities += 1

    if imported_case_ids or imported_activities:
        record_activity(
            user_id,
            "旧数据已导入",
            f"已导入 {len(imported_case_ids)} 个历史案件和 {imported_activities} 条活动记录。",
        )

    return {
        "imported_cases": len(imported_case_ids),
        "imported_activities": imported_activities,
        "case_ids": imported_case_ids,
    }
