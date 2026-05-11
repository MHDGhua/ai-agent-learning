from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import require_current_user
from app.core.persistence import (
    delete_case,
    get_case,
    get_workspace_file,
    list_activities,
    list_cases,
    list_workspace_files,
    list_workspace_knowledge,
    list_workspace_messages,
    record_activity,
    save_case,
    save_workspace_file,
    save_workspace_knowledge,
    save_workspace_message,
)
from app.schemas.workspace import (
    ActivityListResponse,
    WorkspaceConsultRequest,
    WorkspaceConsultResponse,
    WorkspaceDetailResponse,
    WorkspaceFileCreateRequest,
    WorkspaceFileListResponse,
    WorkspaceFileResponse,
    WorkspaceKnowledgeCreateRequest,
    WorkspaceKnowledgeListResponse,
    WorkspaceKnowledgeResponse,
    WorkspaceKnowledgeSearchResponse,
    WorkspaceListResponse,
    WorkspaceMessageListResponse,
    WorkspaceMessageResponse,
    WorkspaceSaveRequest,
    WorkspaceSkillListResponse,
)
from app.services.legal_workspace_assistant import LegalWorkspaceAssistant, get_skill_catalog
from app.services.rag_retriever import retrieve_context


router = APIRouter(prefix="/workspace", tags=["workspace"])
assistant_service = LegalWorkspaceAssistant()


def _require_case(user_id: int, case_id: int):  # type: ignore[no-untyped-def]
    case = get_case(user_id, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="案件不存在。")
    return case


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
    case = _require_case(user["id"], case_id)
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


@router.get("/skills", response_model=WorkspaceSkillListResponse)
async def get_workspace_skills(user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    return WorkspaceSkillListResponse(items=get_skill_catalog())


@router.post("/cases/{case_id}/files", response_model=WorkspaceFileResponse)
async def add_case_file(
    case_id: int,
    request: WorkspaceFileCreateRequest,
    user=Depends(require_current_user),  # type: ignore[no-untyped-def]
):
    case = _require_case(user["id"], case_id)
    if not request.filename.strip():
        raise HTTPException(status_code=422, detail="文件名不能为空。")
    saved = save_workspace_file(
        user["id"],
        case_id,
        filename=request.filename,
        file_type=request.file_type,
        note=request.note,
        content_text=request.content,
    )
    record_activity(user["id"], "文件已加入", f"{request.filename} 已加入 {case['title']}。", case_id=case_id)
    return WorkspaceFileResponse(**saved)


@router.get("/cases/{case_id}/files", response_model=WorkspaceFileListResponse)
async def get_case_files(case_id: int, user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    _require_case(user["id"], case_id)
    return WorkspaceFileListResponse(items=list_workspace_files(user["id"], case_id))


@router.post("/cases/{case_id}/knowledge", response_model=WorkspaceKnowledgeResponse)
async def add_case_knowledge(
    case_id: int,
    request: WorkspaceKnowledgeCreateRequest,
    user=Depends(require_current_user),  # type: ignore[no-untyped-def]
):
    case = _require_case(user["id"], case_id)
    if not request.title.strip() or not request.content.strip():
        raise HTTPException(status_code=422, detail="知识标题和内容不能为空。")
    saved = save_workspace_knowledge(
        user["id"],
        case_id,
        title=request.title,
        source=request.source,
        content_text=request.content,
    )
    record_activity(user["id"], "知识已保存", f"{request.title} 已加入 {case['title']}。", case_id=case_id)
    return WorkspaceKnowledgeResponse(**saved)


@router.get("/cases/{case_id}/knowledge", response_model=WorkspaceKnowledgeListResponse)
async def get_case_knowledge(case_id: int, user=Depends(require_current_user)):  # type: ignore[no-untyped-def]
    _require_case(user["id"], case_id)
    return WorkspaceKnowledgeListResponse(items=list_workspace_knowledge(user["id"], case_id))


@router.get("/knowledge/search", response_model=WorkspaceKnowledgeSearchResponse)
async def search_workspace_knowledge(
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=10),
    user=Depends(require_current_user),  # type: ignore[no-untyped-def]
):
    refs = retrieve_context(query, top_k=limit)
    return {
        "query": query,
        "items": [
            {
                "rank": index + 1,
                "title": (ref.splitlines()[0] if ref else "本地参考")[:120],
                "snippet": ref[:700],
            }
            for index, ref in enumerate(refs)
        ],
    }


@router.get("/cases/{case_id}/messages", response_model=WorkspaceMessageListResponse)
async def get_case_messages(
    case_id: int,
    limit: int = Query(20, ge=1, le=50),
    user=Depends(require_current_user),  # type: ignore[no-untyped-def]
):
    _require_case(user["id"], case_id)
    return WorkspaceMessageListResponse(items=[
        WorkspaceMessageResponse(**item)
        for item in list_workspace_messages(user["id"], case_id, limit=limit)
    ])


@router.post("/cases/{case_id}/consult", response_model=WorkspaceConsultResponse)
async def consult_case_workspace(
    case_id: int,
    request: WorkspaceConsultRequest,
    user=Depends(require_current_user),  # type: ignore[no-untyped-def]
):
    case = _require_case(user["id"], case_id)
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="咨询内容不能为空。")

    selected_files = []
    if request.file_ids:
        for file_id in request.file_ids:
            file_record = get_workspace_file(user["id"], case_id, file_id)
            if file_record is None:
                raise HTTPException(status_code=404, detail=f"文件不存在：{file_id}")
            selected_files.append(file_record)
    else:
        selected_files = list_workspace_files(user["id"], case_id, limit=3)

    knowledge_items = list_workspace_knowledge(user["id"], case_id, limit=8)
    if request.knowledge_query:
        for index, ref in enumerate(retrieve_context(request.knowledge_query, top_k=3)):
            knowledge_items.append({
                "id": -(index + 1),
                "title": (ref.splitlines()[0] if ref else "本地参考")[:120],
                "source": "retrieval",
                "content_text": ref,
                "content_preview": ref[:240],
                "created_at": "",
                "updated_at": "",
            })

    result = await assistant_service.consult(
        case_record=case,
        message=message,
        skill_id=request.skill_id,
        files=selected_files,
        knowledge_items=knowledge_items,
        deep_think=request.deep_think,
        online_search=request.online_search,
    )
    saved_message = save_workspace_message(
        user["id"],
        case_id,
        skill_id=result["skill_id"],
        skill_name=result["skill_name"],
        user_message=message,
        assistant_message=result["assistant_message"],
        summary=result["summary"],
        response_json=result,
    )
    record_activity(
        user["id"],
        "法律助手已回复",
        f"{result['skill_name']} 已完成：{result['summary']}",
        case_id=case_id,
    )
    return WorkspaceConsultResponse(
        case_id=case_id,
        skill_id=result["skill_id"],
        skill_name=result["skill_name"],
        user_message=message,
        assistant_message=result["assistant_message"],
        summary=result["summary"],
        citations=result["citations"],
        next_actions=result["next_actions"],
        pipeline_status=[
            *result["pipeline_status"],
            {"name": "persist_message", "status": "ok", "summary": f"message_id={saved_message['id']}"},
        ],
        related_files=[WorkspaceFileResponse(**item) for item in selected_files],
        related_knowledge=[WorkspaceKnowledgeResponse(**item) for item in knowledge_items if item.get("id", 0) > 0],
    )
