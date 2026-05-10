from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkspaceSaveRequest(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    case_type: str = ""
    primary_finding: str = ""
    readiness: str = ""
    next_best_action: str = ""
    snapshot: Dict[str, Any] = Field(default_factory=dict)


class WorkspaceSummaryResponse(BaseModel):
    id: int
    title: str
    case_type: str
    primary_finding: str
    readiness: str
    next_best_action: str
    created_at: str
    updated_at: str


class WorkspaceDetailResponse(WorkspaceSummaryResponse):
    snapshot: Dict[str, Any] = Field(default_factory=dict)


class ActivityResponse(BaseModel):
    id: int
    title: str
    detail: str
    created_at: str
    case_id: Optional[int] = None


class WorkspaceListResponse(BaseModel):
    items: List[WorkspaceSummaryResponse]


class ActivityListResponse(BaseModel):
    items: List[ActivityResponse]
