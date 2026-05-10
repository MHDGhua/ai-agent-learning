from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import require_current_user
from app.schemas.workspace import (
    ActivityListResponse,
    LegacyImportRequest,
    LegacyImportResponse,
    WorkspaceDetailResponse,
    WorkspaceListResponse,
    WorkspaceSaveRequest,
)
from app.services.workspace_service import (
    get_workspace_case,
    import_legacy_workspace,
    list_workspace_activities,
    list_workspace_cases,
    remove_workspace_case,
    save_workspace_case,
)


router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/cases", response_model=WorkspaceListResponse)
async def get_cases(user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    return WorkspaceListResponse(items=list_workspace_cases(user["id"]))


@router.post("/cases", response_model=WorkspaceDetailResponse)
async def upsert_case(request: WorkspaceSaveRequest, user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    try:
        saved = save_workspace_case(user["id"], request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return WorkspaceDetailResponse(**saved)


@router.get("/cases/{case_id}", response_model=WorkspaceDetailResponse)
async def get_case_detail(case_id: int, user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    case = get_workspace_case(user["id"], case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="案件不存在。")
    return WorkspaceDetailResponse(**case)


@router.delete("/cases/{case_id}", status_code=204)
async def remove_case(case_id: int, user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    deleted = remove_workspace_case(user["id"], case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="案件不存在。")


@router.get("/activities", response_model=ActivityListResponse)
async def get_activity_feed(
    limit: int = Query(12, ge=1, le=50),
    user=Depends(require_current_user),  # type: ignore[no-untyped-def]
):
    return ActivityListResponse(items=list_workspace_activities(user["id"], limit=limit))


@router.post("/import-legacy", response_model=LegacyImportResponse)
async def import_legacy(
    request: LegacyImportRequest,
    user=Depends(require_current_user),  # type: ignore[no-untyped-def]
):
    result = import_legacy_workspace(
        user["id"],
        history_entries=[item.model_dump() for item in request.history_entries],
        activities=[item.model_dump() for item in request.activities],
    )
    return LegacyImportResponse(**result)
