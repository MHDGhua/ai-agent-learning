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


class WorkspaceSkillResponse(BaseModel):
    id: str
    name: str
    description: str
    suggested_use: str
    kind: str


class WorkspaceSkillListResponse(BaseModel):
    items: List[WorkspaceSkillResponse]


class WorkspaceFileCreateRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=160)
    content: str = Field(default="", max_length=120_000)
    file_type: str = Field(default="text/plain", max_length=80)
    note: str = Field(default="", max_length=500)


class WorkspaceFileResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    note: str
    content_preview: str
    created_at: str
    updated_at: str


class WorkspaceFileListResponse(BaseModel):
    items: List[WorkspaceFileResponse]


class WorkspaceKnowledgeCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    content: str = Field(..., min_length=1, max_length=80_000)
    source: str = Field(default="manual", max_length=120)


class WorkspaceKnowledgeResponse(BaseModel):
    id: int
    title: str
    source: str
    content_preview: str
    created_at: str


class WorkspaceKnowledgeListResponse(BaseModel):
    items: List[WorkspaceKnowledgeResponse]


class WorkspaceConsultRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=6_000)
    skill_id: Optional[str] = Field(default=None, max_length=80)
    knowledge_query: Optional[str] = Field(default=None, max_length=500)
    deep_think: bool = False
    online_search: bool = False
    file_ids: List[int] = Field(default_factory=list, max_length=10)


class WorkspaceConsultResponse(BaseModel):
    case_id: int
    skill_id: str
    skill_name: str
    user_message: str
    assistant_message: str
    summary: str
    citations: List[Dict[str, Any]]
    next_actions: List[str]
    pipeline_status: List[Dict[str, Any]]
    related_files: List[WorkspaceFileResponse] = Field(default_factory=list)
    related_knowledge: List[WorkspaceKnowledgeResponse] = Field(default_factory=list)


class WorkspaceMessageResponse(BaseModel):
    id: int
    case_id: int
    skill_id: str
    skill_name: str
    user_message: str
    assistant_message: str
    summary: str
    created_at: str


class WorkspaceMessageListResponse(BaseModel):
    items: List[WorkspaceMessageResponse]


class WorkspaceKnowledgeSearchItem(BaseModel):
    rank: int
    title: str
    snippet: str


class WorkspaceKnowledgeSearchResponse(BaseModel):
    query: str
    items: List[WorkspaceKnowledgeSearchItem]
