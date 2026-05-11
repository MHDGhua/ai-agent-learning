from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.arbitration_analyzer import ArbitrationAnalyzer
from app.services.chongqing_precedent import ChongqingPrecedentAdvisor
from app.services.legal_workflow import LegalWorkflowAnalyzer
from app.services.llm_client import LLMClient
from app.services.rag_retriever import retrieve_context


SKILL_CATALOG: List[Dict[str, str]] = [
    {
        "id": "legal_consult",
        "name": "法律咨询",
        "description": "围绕劳动争议给出下一步建议、管辖判断、缺口提示和应对方向。",
        "suggested_use": "用户描述完纠纷后直接咨询使用。",
        "kind": "consult",
    },
    {
        "id": "file_review",
        "name": "文件审查",
        "description": "审查起诉状、答辩状、代理词或劳动合同，识别风险和缺项。",
        "suggested_use": "上传或粘贴文本文件后使用。",
        "kind": "review",
    },
    {
        "id": "knowledge_search",
        "name": "多维检索",
        "description": "检索法规、案例和重庆本地参考，支持关键词和语义召回。",
        "suggested_use": "需要找法条、案例或本地依据时使用。",
        "kind": "search",
    },
    {
        "id": "hearing_outline",
        "name": "庭审提纲",
        "description": "把案情和文件整理成庭审问答题纲。",
        "suggested_use": "准备庭审、答辩或质证时使用。",
        "kind": "outline",
    },
    {
        "id": "arbitration_workup",
        "name": "仲裁准备",
        "description": "输出案件判断、补证、风险、调解和文书建议。",
        "suggested_use": "需要一体化仲裁准备结果时使用。",
        "kind": "analysis",
    },
]


def get_skill_catalog() -> List[Dict[str, str]]:
    return list(SKILL_CATALOG)


def _clip(value: Any, max_chars: int = 280) -> str:
    text = str(value or "")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def _skill_map() -> Dict[str, Dict[str, str]]:
    return {item["id"]: item for item in SKILL_CATALOG}


def infer_skill_id(message: str, file_records: List[Dict[str, Any]] | None = None) -> str:
    text = f"{message or ''} {' '.join(str(item.get('filename', '')) for item in (file_records or []))}".lower()
    if any(keyword in text for keyword in ["庭审问答", "问答题纲", "提纲", "问答"]):
        return "hearing_outline"
    if any(keyword in text for keyword in ["合同", "起诉状", "答辩状", "代理词", "审查", "文件"]):
        return "file_review"
    if any(keyword in text for keyword in ["检索", "法规", "案例", "知识", "法条"]):
        return "knowledge_search"
    if any(keyword in text for keyword in ["仲裁", "补证", "风险", "胜诉", "管辖", "时效"]):
        return "arbitration_workup"
    return "legal_consult"


class LegalWorkspaceAssistant:
    """Farui-style workspace assistant built on top of the arbitration engine."""

    def __init__(self) -> None:
        self.workflow_analyzer = LegalWorkflowAnalyzer()
        self.arbitration_analyzer = ArbitrationAnalyzer()
        self.precedent_advisor = ChongqingPrecedentAdvisor()
        self.llm_client = LLMClient()

    def build_case_payload(self, case_record: Dict[str, Any], message: str = "") -> Dict[str, Any]:
        snapshot = case_record.get("snapshot") or {}
        case_form = snapshot.get("caseForm") or {}
        applicant_info = dict(case_form.get("applicant_info") or {})
        facts = str(case_form.get("facts") or snapshot.get("facts") or "").strip()
        evidence = [str(item).strip() for item in (snapshot.get("evidence") or case_form.get("evidence") or []) if str(item).strip()]
        case_type = str(case_record.get("case_type") or snapshot.get("caseType") or "").strip()
        if message.strip():
            facts = f"{facts}\n{message.strip()}".strip()
        return {
            "case_type": case_type or "劳动争议",
            "facts": facts or message or "待补充事实",
            "evidence": evidence,
            "applicant_info": applicant_info,
            "salary": case_form.get("applicant_info", {}).get("salary") or snapshot.get("salary") or 0,
            "years": case_form.get("years") or snapshot.get("years") or 0,
            "amount": snapshot.get("amount") or 0,
            "evidence_quality": snapshot.get("evidence_quality") or "一般",
            "applicant_background": snapshot.get("applicant_background") or "普通员工",
        }

    def _case_file_context(self, files: List[Dict[str, Any]]) -> List[str]:
        return [
            f"{item.get('filename', '未命名文件')}：{_clip(item.get('content_text') or item.get('content_preview') or '', 500)}"
            for item in files
        ]

    def _build_citations(self, references: List[str], knowledge_items: List[Dict[str, Any]], files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        citations: List[Dict[str, Any]] = []
        for item in files[:3]:
            citations.append({
                "type": "file",
                "title": item.get("filename", ""),
                "snippet": _clip(item.get("content_preview") or item.get("content_text") or "", 180),
            })
        for item in knowledge_items[:3]:
            citations.append({
                "type": "knowledge",
                "title": item.get("title", ""),
                "snippet": _clip(item.get("content_preview") or item.get("content_text") or "", 180),
                "source": item.get("source", ""),
            })
        for ref in references[:3]:
            citations.append({
                "type": "reference",
                "title": _clip(ref.splitlines()[0] if ref else "重庆本地参考", 100),
                "snippet": _clip(ref, 180),
            })
        return citations

    async def consult(
        self,
        *,
        case_record: Dict[str, Any],
        message: str,
        skill_id: Optional[str] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        knowledge_items: Optional[List[Dict[str, Any]]] = None,
        deep_think: bool = False,
        online_search: bool = False,
    ) -> Dict[str, Any]:
        files = files or []
        knowledge_items = knowledge_items or []
        requested_skill_id = skill_id or infer_skill_id(message, files)
        skills = _skill_map()
        resolved_skill_id = requested_skill_id if requested_skill_id in skills else "legal_consult"
        skill_meta = skills[resolved_skill_id]
        skill_summary = skill_meta["name"]
        skill_status = "ok"
        if requested_skill_id != resolved_skill_id:
            skill_summary = f"未知技能 {requested_skill_id}，已按法律咨询处理"
            skill_status = "warning"
        case_payload = self.build_case_payload(case_record, message)
        references = retrieve_context(f"{case_payload['case_type']} {message}", top_k=5 if deep_think or online_search else 3)
        workflow = self.workflow_analyzer.analyze(case_payload)
        local_reference = self.precedent_advisor.build_local_reference(case_payload)
        citations = self._build_citations(references, knowledge_items, files)
        next_actions = list(dict.fromkeys((workflow.action_plan or [])[:5] + (local_reference.get("reference_strategy") or [])[:3]))

        assistant_message = self._compose_reply(
            skill_id=resolved_skill_id,
            case_payload=case_payload,
            workflow=workflow,
            local_reference=local_reference,
            files=files,
            knowledge_items=knowledge_items,
            references=references,
            message=message,
            deep_think=deep_think,
            online_search=online_search,
        )

        llm_enabled = not getattr(self.llm_client, "_use_local_logic", lambda: True)()
        if llm_enabled:
            assistant_message = await self._llm_refine(
                skill_meta=skill_meta,
                case_payload=case_payload,
                assistant_message=assistant_message,
                references=references,
                files=files,
                knowledge_items=knowledge_items,
            ) or assistant_message

        return {
            "skill_id": resolved_skill_id,
            "skill_name": skill_meta["name"],
            "assistant_message": assistant_message,
            "summary": self._summarize_reply(skill_meta["name"], workflow, local_reference),
            "citations": citations,
            "next_actions": next_actions[:6],
            "pipeline_status": [
                {"name": "resolve_skill", "status": skill_status, "summary": skill_summary},
                {"name": "load_case", "status": "ok", "summary": case_payload["case_type"]},
                {"name": "load_files", "status": "ok", "summary": f"{len(files)} files"},
                {"name": "run_skill", "status": "ok", "summary": skill_meta["name"]},
                {"name": "load_references", "status": "ok", "summary": f"{len(references)} refs"},
                {"name": "compose_reply", "status": "ok", "summary": "reply ready"},
            ],
            "related_files": files,
            "related_knowledge": knowledge_items,
            "case_payload": case_payload,
        }

    def _compose_reply(
        self,
        *,
        skill_id: str,
        case_payload: Dict[str, Any],
        workflow: Any,
        local_reference: Dict[str, Any],
        files: List[Dict[str, Any]],
        knowledge_items: List[Dict[str, Any]],
        references: List[str],
        message: str,
        deep_think: bool,
        online_search: bool,
    ) -> str:
        lines: List[str] = []
        if skill_id == "file_review":
            lines.append("我先按文件审查方式看。")
            if files:
                for item in files[:3]:
                    issues = self._review_file_text(item.get("content_text") or item.get("content_preview") or "", case_payload)
                    if issues:
                        lines.append(f"文件《{item.get('filename', '未命名')}》：{'；'.join(issues[:3])}")
                    else:
                        lines.append(f"文件《{item.get('filename', '未命名')}》：结构基本可用，建议继续补齐当事人信息、时间和金额。")
            else:
                lines.append("当前没有文件，先上传合同、起诉状、答辩状或代理词文本。")
            lines.append("可继续检查文件中的当事人、日期、金额、证据和请求是否一致。")
        elif skill_id == "knowledge_search":
            lines.append("我先按检索方式整理。")
            if references:
                lines.append("本地检索结果：")
                for ref in references[:3]:
                    lines.append(f"- {ref.splitlines()[0] if ref else '重庆本地参考'}")
            else:
                lines.append("暂时没有召回到足够的本地资料，建议换个更具体的关键词。")
            if knowledge_items:
                lines.append("你当前项目里的知识条目也可以一起参考。")
        elif skill_id == "hearing_outline":
            lines.append("我先按庭审问答题纲整理。")
            outline = self._build_hearing_outline(case_payload, workflow, files)
            lines.extend(outline)
        elif skill_id == "arbitration_workup":
            lines.append("我先按仲裁准备方式整理。")
            lines.extend(self._build_workup_reply(case_payload, workflow, local_reference, references))
        else:
            lines.append("我先按法律咨询方式回答。")
            lines.extend(self._build_consult_reply(case_payload, workflow, local_reference, references, files, knowledge_items, deep_think, online_search))

        if message.strip():
            lines.insert(0, f"你问的是：{_clip(message, 140)}")
        return "\n".join([line for line in lines if line])

    def _build_consult_reply(
        self,
        case_payload: Dict[str, Any],
        workflow: Any,
        local_reference: Dict[str, Any],
        references: List[str],
        files: List[Dict[str, Any]],
        knowledge_items: List[Dict[str, Any]],
        deep_think: bool,
        online_search: bool,
    ) -> List[str]:
        lines = [
            f"案件类型：{case_payload.get('case_type', '劳动争议')}",
            f"初步判断：{workflow.jurisdiction.get('suggested_forum') or '需要补充管辖信息后再确认'}。",
            f"时效状态：{workflow.limitation.get('status') or '待判断'}。",
        ]
        if workflow.claim_items:
            claim_text = "；".join(item.get("name", "") for item in workflow.claim_items[:4])
            lines.append(f"可考虑的请求：{claim_text}。")
        if workflow.warnings:
            lines.append(f"风险提示：{'；'.join(workflow.warnings[:3])}。")
        if files:
            lines.append(f"已接入 {len(files)} 份文件，可进一步核对证据链。")
        if knowledge_items:
            lines.append(f"项目内已有 {len(knowledge_items)} 条知识条目可用。")
        if references:
            lines.append(f"本地参考已召回 {len(references)} 条。")
        if deep_think:
            lines.append("当前为深度整理模式，我会把缺口和对方可能的抗辩点再展开一层。")
        if online_search:
            lines.append("当前为扩展检索模式，已尽量扩大本地资料召回范围。")
        if local_reference.get("reference_strategy"):
            lines.append(f"建议：{'；'.join(local_reference.get('reference_strategy', [])[:3])}。")
        return lines

    def _build_workup_reply(
        self,
        case_payload: Dict[str, Any],
        workflow: Any,
        local_reference: Dict[str, Any],
        references: List[str],
    ) -> List[str]:
        lines = [
            f"当前案件：{case_payload.get('case_type', '劳动争议')}",
            f"重点关注：{workflow.jurisdiction.get('suggested_forum') or '管辖待补齐'} / {workflow.limitation.get('status') or '时效待核查'}。",
        ]
        if workflow.claim_items:
            lines.append("已识别的请求项：")
            for item in workflow.claim_items[:4]:
                lines.append(f"- {item.get('name', '')}：{item.get('calculation', '')}")
        if workflow.evidence_checklist:
            lines.append("证据缺口：")
            for block in workflow.evidence_checklist[:2]:
                lines.append(f"- {block.get('category', '')}: {', '.join(block.get('items', [])[:3])}")
        if references:
            lines.append("本地参考可继续补充。")
        if local_reference.get("reference_strategy"):
            lines.append(f"处理建议：{'；'.join(local_reference.get('reference_strategy', [])[:3])}")
        return lines

    def _build_hearing_outline(
        self,
        case_payload: Dict[str, Any],
        workflow: Any,
        files: List[Dict[str, Any]],
    ) -> List[str]:
        lines = [
            f"1. 先确认劳动关系和争议时间线：{case_payload.get('case_type', '劳动争议')}。",
            "2. 逐项确认工资、岗位、工作地点、入职时间和解除时间。",
            "3. 逐项确认证据来源、证明目的、原件是否在手。",
        ]
        if workflow.claim_items:
            lines.append("4. 围绕请求项提问：")
            for item in workflow.claim_items[:4]:
                lines.append(f"   - {item.get('name', '')} 对应的证据和金额口径是什么。")
        if files:
            lines.append("5. 围绕文件内容提问：")
            for item in files[:3]:
                lines.append(f"   - 《{item.get('filename', '未命名')}》中最关键的事实和缺口是什么。")
        lines.append("6. 对方可能会争辩的点：时效、管辖、证据不足、金额不清。")
        return lines

    def _review_file_text(self, text: str, case_payload: Dict[str, Any]) -> List[str]:
        issues: List[str] = []
        content = text or ""
        if not content.strip():
            return ["文件内容为空或无法识别。"]
        if case_payload.get("case_type") and case_payload["case_type"] not in content and len(content) > 80:
            issues.append("文件标题或正文未明显体现案件类型。")
        if "工资" in case_payload.get("case_type", "") or "工资" in case_payload.get("facts", ""):
            if not any(keyword in content for keyword in ["工资", "薪资", "报酬"]):
                issues.append("文件未明显体现工资或劳动报酬信息。")
        if any(keyword in case_payload.get("case_type", "") for keyword in ["解除", "辞退"]):
            if not any(keyword in content for keyword in ["解除", "辞退", "离职"]):
                issues.append("文件未明显体现解除或离职信息。")
        if any(keyword in case_payload.get("case_type", "") for keyword in ["工伤", "受伤"]):
            if not any(keyword in content for keyword in ["工伤", "受伤", "诊断", "就医"]):
                issues.append("文件未明显体现工伤或就医材料。")
        if "合同" in content and not any(keyword in content for keyword in ["甲方", "乙方", "期限", "岗位", "工资"]):
            issues.append("合同条款信息偏少，建议补齐当事人、期限、岗位和工资条款。")
        return issues

    def _summarize_reply(self, skill_name: str, workflow: Any, local_reference: Dict[str, Any]) -> str:
        parts = [skill_name, workflow.risk_level.value if getattr(workflow, "risk_level", None) else ""]
        if workflow.warnings:
            parts.append(workflow.warnings[0])
        if local_reference.get("priority"):
            parts.append(str(local_reference.get("priority")))
        return " / ".join([part for part in parts if part])

    async def _llm_refine(
        self,
        *,
        skill_meta: Dict[str, str],
        case_payload: Dict[str, Any],
        assistant_message: str,
        references: List[str],
        files: List[Dict[str, Any]],
        knowledge_items: List[Dict[str, Any]],
    ) -> str:
        prompt = (
            "你是一个法律工作台的助手，只需润色并压缩为适合普通用户阅读的中文回复。\n"
            f"技能：{skill_meta['name']}\n"
            f"案件类型：{case_payload.get('case_type', '')}\n"
            f"事实：{_clip(case_payload.get('facts', ''), 1200)}\n"
            f"文件：{_clip('；'.join(item.get('filename', '') for item in files[:3]), 240)}\n"
            f"知识：{_clip('；'.join(item.get('title', '') for item in knowledge_items[:3]), 240)}\n"
            f"本地参考：{_clip('；'.join(ref.splitlines()[0] if ref else '' for ref in references[:3]), 240)}\n"
            f"草稿回复：{_clip(assistant_message, 1600)}\n"
            "要求：保留结论、风险、下一步，去掉冗余内容，输出纯文本。"
        )
        try:
            refined = await self.llm_client.generate_text(prompt)
            refined = refined.strip()
            return refined or assistant_message
        except Exception:
            return assistant_message
