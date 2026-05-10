from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import require_current_user
from app.core.persistence import delete_case, get_case, list_activities, list_cases, record_activity, save_case
from app.schemas.workspace import (
    ActivityListResponse,
    WorkspaceDetailResponse,
    WorkspaceListResponse,
    WorkspaceSaveRequest,
)


router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/cases", response_model=WorkspaceListResponse)
async def get_cases(user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    return WorkspaceListResponse(items=list_cases(user["id"]))


@router.post("/cases", response_model=WorkspaceDetailResponse)
async def upsert_case(request: WorkspaceSaveRequest, user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    try:
        saved = save_case(user["id"], request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    record_activity(
        user["id"],
        "案件已保存",
        f"{saved['title']} 已保存到服务端。",
        case_id=saved["id"],
    )
    return WorkspaceDetailResponse(**saved)


@router.get("/cases/{case_id}", response_model=WorkspaceDetailResponse)
async def get_case_detail(case_id: int, user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    case = get_case(user["id"], case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="案件不存在。")
    return WorkspaceDetailResponse(**case)


@router.delete("/cases/{case_id}", status_code=204)
async def remove_case(case_id: int, user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    deleted = delete_case(user["id"], case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="案件不存在。")
    record_activity(user["id"], "案件已删除", f"案件 #{case_id} 已从服务端移除。")


@router.get("/activities", response_model=ActivityListResponse)
async def get_activity_feed(
    limit: int = Query(12, ge=1, le=50),
    user=Depends(require_current_user),  # type: ignore[no-untyped-def]
):
    return ActivityListResponse(items=list_activities(user["id"], limit=limit))
