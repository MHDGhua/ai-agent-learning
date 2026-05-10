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


class LegacyHistoryEntry(BaseModel):
    id: Optional[int | str] = None
    kind: str = ""
    kindLabel: str = ""
    title: str = "未命名案件"
    time: str = ""
    readiness: str = ""
    primaryFinding: str = ""
    nextBestAction: str = ""
    caseForm: Dict[str, Any] = Field(default_factory=dict)
    evidenceText: str = ""
    uploadedFiles: List[str] = Field(default_factory=list)
    workupResult: Optional[Dict[str, Any]] = None
    documentResult: Optional[Dict[str, Any]] = None
    documentValidation: Optional[Dict[str, Any]] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)


class LegacyActivityEntry(BaseModel):
    id: Optional[int | str] = None
    title: str
    detail: str
    created_at: Optional[str] = None


class LegacyImportRequest(BaseModel):
    history_entries: List[LegacyHistoryEntry] = Field(default_factory=list)
    activities: List[LegacyActivityEntry] = Field(default_factory=list)


class LegacyImportResponse(BaseModel):
    imported_cases: int
    imported_activities: int
    case_ids: List[int] = Field(default_factory=list)
