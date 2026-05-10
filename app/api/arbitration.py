#!/usr/bin/env python3
"""
劳动仲裁相关API接口
提供仲裁文书生成、案件分析、风险评估等接口
"""

from typing import Dict, Any, List, Optional
from dataclasses import asdict, is_dataclass
from datetime import datetime
import time
from fastapi import APIRouter, HTTPException, Query
from pydantic import Field
from loguru import logger

from app.schemas.arbitration import (
    ArbitrationCostEstimate,
    CaseAnalysisRequest,
    CaseAnalysisResponse,
    CaseWorkupResponse,
    ClaimCalculationRequest,
    ClaimCalculationResponse,
    DocumentGenerationRequest,
    DocumentGenerationResponse,
    DocumentValidationRequest,
    DocumentValidationResponse,
    IntakeChecklistRequest,
    IntakeChecklistResponse,
    LocalReferenceResponse,
    SuccessRatePrediction,
)
from app.core.exceptions import CalculationError, DocumentGenerationError
from app.services.arbitration_document_generator import ArbitrationDocumentGenerator, DocumentType
from app.services.arbitration_analyzer import ArbitrationAnalyzer, ArbitrationAnalysis
from app.services.chongqing_calculator import ChongqingLaborCalculator
from app.services.legal_workflow import LegalWorkflowAnalyzer
from app.services.rag_retriever import retrieve_context
from app.services.llm_client import LLMClient
from app.services.observability import langsmith_status, traceable_case
from app.services.document_post_processor import DocumentPostProcessor
from app.agents.coordinator import CoordinatorAgent
from app.services.api_factory import APIFactory
from app.config.combined_config import API_CLIENT_CONFIG


# 创建API路由器
router = APIRouter(prefix="/arbitration", tags=["arbitration"])


def _validate_document_content(document_type: str, case_data: Dict[str, Any], content: str) -> DocumentValidationResponse:
    applicant_info = case_data.get("applicant_info") or {}
    facts = str(case_data.get("facts") or "")
    evidence = [str(item) for item in case_data.get("evidence") or [] if str(item).strip()]
    issues: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []

    applicant_name = str(applicant_info.get("name") or "").strip()
    employer_name = str(applicant_info.get("employer_name") or "").strip()
    salary = case_data.get("salary") or applicant_info.get("salary")
    amount = case_data.get("amount")

    if applicant_name and applicant_name not in content:
        issues.append("文书中未体现申请人姓名。")
    if employer_name and employer_name not in content:
        issues.append("文书中未体现被申请人名称。")
    if facts and len(facts) > 30 and facts[:20] not in content:
        warnings.append("文书未明显引用案情原文，建议核对事实段。")
    if evidence and not any(item in content for item in evidence[:3]):
        warnings.append("文书未明显引用现有证据名称，建议补入证据目录。")
    if amount and str(int(float(amount))) not in content and str(amount) not in content:
        warnings.append("请求金额未在文书中明显出现，建议复核计算结果。")
    if salary and str(int(float(salary))) not in content and str(salary) not in content:
        warnings.append("工资基数未在文书中明显出现，建议复核。")
    if "《" not in content or "》" not in content:
        warnings.append("未发现法条引用，建议补入适用依据。")

    if document_type == "庭前调解申请书":
        if "调解" not in content:
            issues.append("调解申请书未体现调解请求。")
        suggestions.append("若可接受，优先写明可调解金额和付款期限。")

    is_valid = not issues
    if not suggestions:
        suggestions.extend([
            "核对当事人名称、地址、联系电话一致。",
            "核对金额、工资基数和证据目录一致。",
        ])

    return DocumentValidationResponse(
        document_type=document_type,
        is_valid=is_valid,
        issues=issues,
        warnings=warnings,
        suggestions=suggestions,
        checked_at=datetime.now().isoformat(),
    )


def _build_analysis_summary(analysis: ArbitrationAnalysis) -> str:
    return (
        f"案件类型为{analysis.case_type}，初步风险等级为{analysis.risk_level.value}，"
        f"成功率评估为{analysis.success_probability.value}。"
        f"主要建议：{'；'.join(analysis.recommendations[:3]) if analysis.recommendations else '请补充证据并核实仲裁时效'}。"
        "本结果仅供劳动仲裁准备参考，不构成正式法律意见。"
    )


def _format_local_references(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    docs = retrieve_context(query, top_k=limit)
    references = []
    for doc in docs:
        lines = [line.strip() for line in doc.splitlines() if line.strip()]
        title = ""
        source = ""
        url = ""
        summary_parts = []
        for line in lines:
            if line.startswith("标题:"):
                title = line.replace("标题:", "", 1).strip()
            elif line.startswith("重庆本地参考:"):
                title = line.replace("重庆本地参考:", "", 1).strip()
            elif line.startswith("发布/来源机构:") or line.startswith("来源:"):
                source = line.split(":", 1)[-1].strip()
            elif line.startswith("来源链接:") or line.startswith("链接:"):
                url = line.split(":", 1)[-1].strip()
            elif line.startswith("文件名:"):
                title = line.split(":", 1)[-1].strip()
            elif line.startswith("资料来源:"):
                source = line.split(":", 1)[-1].strip()
            elif line.startswith("摘要:") or line.startswith("要点:") or line.startswith("-"):
                summary_parts.append(line)
            elif line.startswith("内容摘要片段:"):
                summary_parts.append(line.replace("内容摘要片段:", "摘要:", 1))
        references.append({
            "title": title or "重庆本地劳动争议参考",
            "source": source,
            "url": url,
            "summary": " ".join(summary_parts)[:700],
            "raw": doc[:1200],
        })
    return references


def _suggest_document_types(analysis: ArbitrationAnalysis) -> List[str]:
    claim_names = " ".join(item.get("name", "") for item in analysis.claim_items or [])
    return _suggest_document_types_from_claim_names(claim_names)


def _suggest_document_types_from_claim_names(claim_names: str) -> List[str]:
    docs = ["证据清单", "仲裁申请书", "庭前调解申请书"]
    if "解除" in claim_names or "赔偿" in claim_names:
        docs.append("解除事实时间线")
    if "工伤" in claim_names:
        docs.append("工伤证据目录")
    return docs


def _build_service_recommendation(
    request: CaseAnalysisRequest,
    analysis: CaseAnalysisResponse,
    intake: IntakeChecklistResponse,
    prediction: SuccessRatePrediction,
) -> Dict[str, Any]:
    """面向产品/商业闭环的合规服务建议，不替代律师判断。"""
    missing_count = len(intake.missing_questions or [])
    warnings = analysis.warnings or []
    urgent_signals = []
    if analysis.limitation and analysis.limitation.get("status") == "possibly_expired":
        urgent_signals.append("可能超过或接近仲裁时效")
    if not analysis.jurisdiction or not analysis.jurisdiction.get("likely_chongqing_jurisdiction"):
        urgent_signals.append("重庆管辖依据不足")
    if any("工伤" in item.get("name", "") for item in analysis.claim_items or []):
        urgent_signals.append("工伤案件需核查认定和鉴定节点")

    if urgent_signals:
        tier = "建议尽快人工复核"
    elif missing_count >= 3 or warnings:
        tier = "先补材料后复核"
    elif prediction.probability_value >= 0.65:
        tier = "适合进入材料准备"
    else:
        tier = "适合低成本初筛"

    has_contact = bool(request.contact_name or request.contact_phone)
    handoff_materials = ["案件时间线", "仲裁请求及金额明细", "证据目录", "重庆本地参考依据"]
    if analysis.local_reference:
        handoff_materials.append("本地案例匹配摘要")

    return {
        "tier": tier,
        "urgency_signals": urgent_signals,
        "lead_ready": has_contact and missing_count <= 2,
        "missing_count": missing_count,
        "handoff_materials": handoff_materials,
        "next_best_action": "立即安排人工复核" if urgent_signals else ("补齐关键信息" if missing_count else "生成申请书和证据清单"),
        "compliance_notes": [
            "本系统只提供劳动仲裁准备信息和风险提示，不承诺结果。",
            "涉及时效、解除合法性、工伤待遇、较大金额争议时，应由具备资质的律师或法律服务人员复核。",
            "案例与指导意见仅作类案参考，不能直接等同于本案裁判结论。",
        ],
    }


class PipelineTracker:
    """Small per-request pipeline tracker for backend observability."""

    def __init__(self) -> None:
        self._start = time.perf_counter()
        self.steps: List[Dict[str, Any]] = []

    def record(
        self,
        name: str,
        status: str = "ok",
        summary: str = "",
        warnings: Optional[List[str]] = None,
    ) -> None:
        self.steps.append({
            "name": name,
            "status": status,
            "elapsed_ms": round((time.perf_counter() - self._start) * 1000, 2),
            "summary": summary,
            "warnings": warnings or [],
        })


@router.post("/analyze", response_model=CaseAnalysisResponse)
@traceable_case("arbitration.analyze")
async def analyze_case(request: CaseAnalysisRequest) -> CaseAnalysisResponse:
    """
    分析案件情况，提供风险评估、成本估算和成功率预测
    
    Args:
        request: 案件分析请求
        
    Returns:
        案件分析结果
    """
    try:
        # 获取默认API客户端
        api_client_type = API_CLIENT_CONFIG.get("default", "local")
        api_client = APIFactory.create_api_client(api_client_type)
        
        # 如果是外部API，调用外部服务
        if api_client_type != "local":
            # 调用外部API
            result = await api_client.call("/api/arbitration/analyze", request.model_dump())
            return result
        else:
            # 本地处理
            logger.info(f"开始分析案件: {request.case_type}")
            
            # 调用仲裁分析服务
            analyzer = ArbitrationAnalyzer()
            
            # 如果启用了对抗审查，则创建协调器
            coordinator = None
            if request.enable_opposition_review:
                from app.services.llm_client import LLMClient
                llm_client = LLMClient()
                coordinator = CoordinatorAgent(llm_client, None)
            
            analysis = await analyzer.analyze_case(request.model_dump(), coordinator)
            
            # 转换为响应模型
            opposition_review = analysis.opposition_review
            if is_dataclass(opposition_review):
                opposition_review = asdict(opposition_review)

            summary = _build_analysis_summary(analysis)
            analysis_payload = {
                "summary": summary,
                "case_type": analysis.case_type,
                "risk_level": analysis.risk_level.value,
                "risk_factors": analysis.risk_factors,
                "cost_estimate": analysis.cost_estimate,
                "success_probability": analysis.success_probability.value,
                "probability_confidence": analysis.probability_confidence,
                "legal_basis": analysis.legal_basis,
                "case_similarity": analysis.case_similarity,
                "recommendations": analysis.recommendations,
                "missing_info": analysis.missing_info,
                "opposition_review": opposition_review,
                "jurisdiction": analysis.jurisdiction,
                "limitation": analysis.limitation,
                "claim_items": analysis.claim_items,
                "evidence_checklist": analysis.evidence_checklist,
                "action_plan": analysis.action_plan,
                "negotiation_points": analysis.negotiation_points,
                "warnings": analysis.warnings,
                "local_reference": analysis.local_reference,
            }

            response = CaseAnalysisResponse(
                case_type=analysis.case_type,
                risk_level=analysis.risk_level.value,
                risk_factors=analysis.risk_factors,
                cost_estimate=analysis.cost_estimate,
                success_probability=analysis.success_probability.value,
                probability_confidence=analysis.probability_confidence,
                legal_basis=analysis.legal_basis,
                case_similarity=analysis.case_similarity,
                recommendations=analysis.recommendations,
                missing_info=analysis.missing_info,
                opposition_review=opposition_review,
                jurisdiction=analysis.jurisdiction,
                limitation=analysis.limitation,
                claim_items=analysis.claim_items,
                evidence_checklist=analysis.evidence_checklist,
                action_plan=analysis.action_plan,
                negotiation_points=analysis.negotiation_points,
                warnings=analysis.warnings,
                local_reference=analysis.local_reference,
                summary=summary,
                analysis=analysis_payload,
            )
            
            logger.info(f"案件分析完成: {request.case_type}")
            return response
        
    except Exception:
        logger.exception("案件分析失败")
        raise HTTPException(status_code=500, detail="案件分析失败，请稍后重试。")


@traceable_case("arbitration.analyze_local")
async def _analyze_case_local(request: CaseAnalysisRequest) -> CaseAnalysisResponse:
    analyzer = ArbitrationAnalyzer()
    coordinator = None
    if request.enable_opposition_review:
        llm_client = LLMClient()
        coordinator = CoordinatorAgent(llm_client, None)
    analysis = await analyzer.analyze_case(request.model_dump(), coordinator)
    opposition_review = analysis.opposition_review
    if is_dataclass(opposition_review):
        opposition_review = asdict(opposition_review)
    summary = _build_analysis_summary(analysis)
    analysis_payload = {
        "summary": summary,
        "case_type": analysis.case_type,
        "risk_level": analysis.risk_level.value,
        "risk_factors": analysis.risk_factors,
        "cost_estimate": analysis.cost_estimate,
        "success_probability": analysis.success_probability.value,
        "probability_confidence": analysis.probability_confidence,
        "legal_basis": analysis.legal_basis,
        "case_similarity": analysis.case_similarity,
        "recommendations": analysis.recommendations,
        "missing_info": analysis.missing_info,
        "opposition_review": opposition_review,
        "jurisdiction": analysis.jurisdiction,
        "limitation": analysis.limitation,
        "claim_items": analysis.claim_items,
        "evidence_checklist": analysis.evidence_checklist,
        "action_plan": analysis.action_plan,
        "negotiation_points": analysis.negotiation_points,
        "warnings": analysis.warnings,
        "local_reference": analysis.local_reference,
    }
    return CaseAnalysisResponse(
        case_type=analysis.case_type,
        risk_level=analysis.risk_level.value,
        risk_factors=analysis.risk_factors,
        cost_estimate=analysis.cost_estimate,
        success_probability=analysis.success_probability.value,
        probability_confidence=analysis.probability_confidence,
        legal_basis=analysis.legal_basis,
        case_similarity=analysis.case_similarity,
        recommendations=analysis.recommendations,
        missing_info=analysis.missing_info,
        opposition_review=opposition_review,
        jurisdiction=analysis.jurisdiction,
        limitation=analysis.limitation,
        claim_items=analysis.claim_items,
        evidence_checklist=analysis.evidence_checklist,
        action_plan=analysis.action_plan,
        negotiation_points=analysis.negotiation_points,
        warnings=analysis.warnings,
        local_reference=analysis.local_reference,
        summary=summary,
        analysis=analysis_payload,
    )


@router.post("/generate-document", response_model=DocumentGenerationResponse)
@traceable_case("arbitration.generate_document")
async def generate_document(request: DocumentGenerationRequest) -> DocumentGenerationResponse:
    """
    生成劳动仲裁文书
    
    Args:
        request: 文书生成请求
        
    Returns:
        生成的文书内容
    """
    try:
        logger.info(f"开始生成文书: {request.document_type}")
        
        # 获取默认API客户端
        api_client_type = API_CLIENT_CONFIG.get("default", "local")
        api_client = APIFactory.create_api_client(api_client_type)
        
        # 如果是外部API，调用外部服务
        if api_client_type != "local":
            # 调用外部API
            result = await api_client.call("/api/arbitration/generate-document", request.model_dump())
            return result
        else:
            # 验证文书类型
            try:
                doc_type = DocumentType(request.document_type)
            except ValueError:
                raise DocumentGenerationError(
                    f"不支持的文书类型: {request.document_type}",
                    detail=f"支持的类型: {[t.value for t in DocumentType]}"
                )
            
            # 调用文书生成服务
            generator = ArbitrationDocumentGenerator()
            content = await generator.generate_arbitration_document(doc_type, request.case_data)

            # 后处理校验
            post_processor = DocumentPostProcessor()
            pp_report = post_processor.validate(content, request.document_type, request.case_data)
            pp_warnings = pp_report.warnings + pp_report.errors

            advice_parts = [f"已生成{request.document_type}，请核对当事人信息、仲裁请求金额和证据页码后使用。"]
            if pp_warnings:
                advice_parts.append("自动校验发现：" + "；".join(pp_warnings[:3]))

            # 构造响应
            response = DocumentGenerationResponse(
                document_type=request.document_type,
                content=content,
                generated_at=datetime.now().isoformat(),
                advice="".join(advice_parts),
                document={"document_type": request.document_type, "content": content}
            )
            
            logger.info(f"文书生成完成: {request.document_type}")
            return response
        
    except Exception:
        logger.exception("文书生成失败")
        raise HTTPException(status_code=500, detail="文书生成失败，请稍后重试。")


@router.post("/validate-document", response_model=DocumentValidationResponse)
@traceable_case("arbitration.validate_document")
async def validate_document(request: DocumentValidationRequest) -> DocumentValidationResponse:
    """校验文书内容是否和案件信息一致。"""
    return _validate_document_content(request.document_type, request.case_data, request.content)


@router.get("/observability/langsmith")
async def get_langsmith_status() -> Dict[str, Any]:
    """查看 LangSmith 追踪配置状态，不返回密钥。"""
    return langsmith_status()


@router.post("/estimate-cost", response_model=ArbitrationCostEstimate)
async def estimate_cost(request: CaseAnalysisRequest) -> ArbitrationCostEstimate:
    """
    估算仲裁成本
    
    Args:
        request: 案件信息
        
    Returns:
        成本估算结果
    """
    try:
        logger.info(f"开始估算仲裁成本")
        
        # 获取默认API客户端
        api_client_type = API_CLIENT_CONFIG.get("default", "local")
        api_client = APIFactory.create_api_client(api_client_type)
        
        # 如果是外部API，调用外部服务
        if api_client_type != "local":
            # 调用外部API
            result = await api_client.call("/api/arbitration/estimate-cost", request.model_dump())
            return result
        else:
            # 调用成本估算服务
            analyzer = ArbitrationAnalyzer()
            cost_estimate = await analyzer.estimate_cost(request.model_dump())
            
            # 转换为响应模型
            response = ArbitrationCostEstimate(
                **cost_estimate,
                cost_estimate=cost_estimate["total_cost"],
                explanation="劳动争议仲裁不收费；这里主要估算律师费、复印交通等准备成本。"
            )
            
            logger.info("仲裁成本估算完成")
            return response
        
    except Exception:
        logger.exception("成本估算失败")
        raise HTTPException(status_code=500, detail="成本估算失败，请稍后重试。")


@router.post("/predict-success-rate", response_model=SuccessRatePrediction)
async def predict_success_rate(request: CaseAnalysisRequest) -> SuccessRatePrediction:
    """
    预测仲裁成功率
    
    Args:
        request: 案件信息
        
    Returns:
        成功率预测结果
    """
    try:
        logger.info(f"开始预测仲裁成功率")
        
        # 获取默认API客户端
        api_client_type = API_CLIENT_CONFIG.get("default", "local")
        api_client = APIFactory.create_api_client(api_client_type)
        
        # 如果是外部API，调用外部服务
        if api_client_type != "local":
            # 调用外部API
            result = await api_client.call("/api/arbitration/predict-success-rate", request.model_dump())
            return result
        else:
            # 调用成功率预测服务
            analyzer = ArbitrationAnalyzer()
            prediction = await analyzer.predict_success_rate(request.model_dump())
            
            # 转换为响应模型
            response = SuccessRatePrediction(
                success_probability=prediction["success_probability"],
                probability_value=prediction["probability_value"],
                confidence=prediction["confidence"],
                key_factors=prediction["key_factors"],
                success_rate=prediction["success_probability"],
                explanation="预测值基于证据质量、证据数量和劳动者背景等规则因子，不能替代仲裁委最终裁判。"
            )
            
            logger.info("仲裁成功率预测完成")
            return response
        
    except Exception:
        logger.exception("成功率预测失败")
        raise HTTPException(status_code=500, detail="成功率预测失败，请稍后重试。")


@router.post("/calculate-claim", response_model=ClaimCalculationResponse)
async def calculate_claim(request: ClaimCalculationRequest) -> ClaimCalculationResponse:
    """
    计算常见劳动仲裁金额：经济补偿/违法解除赔偿、加班费、工伤一次性伤残补助金。
    """
    try:
        calculator = ChongqingLaborCalculator()
        calculation_type = request.calculation_type
        notes = ["计算结果仅供准备仲裁请求时复核，最终金额需结合工资基数、证据和当地最新口径确认。"]

        if calculation_type in {"severance", "经济补偿", "赔偿金", "违法解除"}:
            amount = calculator.calculate_severance(request.salary, request.years, request.reason)
            multiplier = "2N" if "违法" in request.reason or calculation_type in {"赔偿金", "违法解除"} else "N"
            return ClaimCalculationResponse(
                calculation_type=calculation_type,
                amount=amount,
                formula=f"min(月工资, 当地上年度职工月平均工资3倍) × 折算工作年限 × {multiplier}",
                notes=notes + ["工作年限已按不满半年0.5、满半年不满一年1进行折算。"],
            )

        if calculation_type in {"overtime", "加班费"}:
            amount = calculator.calculate_overtime(request.hours, request.day_type, request.salary)
            return ClaimCalculationResponse(
                calculation_type=calculation_type,
                amount=round(amount, 2),
                formula=f"月工资 ÷ 21.75 ÷ 8 × 加班小时 × {request.day_type}倍率",
                notes=notes + ["平日、休息日、法定节假日倍率不同，需按考勤分别计算。"],
            )

        if calculation_type in {"work_injury", "工伤"}:
            if request.injury_level is None:
                raise HTTPException(status_code=400, detail="计算工伤待遇需要提供 injury_level")
            amount = calculator.calculate_work_injury(request.injury_level, request.salary)
            return ClaimCalculationResponse(
                calculation_type=calculation_type,
                amount=round(amount, 2),
                formula="本人工资 × 伤残等级对应月数",
                notes=notes + ["这里只计算一次性伤残补助金，未包含医疗费、停工留薪期工资等其他项目。"],
            )

        raise HTTPException(status_code=400, detail=f"不支持的计算类型: {calculation_type}")

    except HTTPException:
        raise
    except Exception:
        logger.exception("金额计算失败")
        raise HTTPException(status_code=500, detail="金额计算失败，请稍后重试。")


@router.post("/intake-checklist", response_model=IntakeChecklistResponse)
async def intake_checklist(request: IntakeChecklistRequest) -> IntakeChecklistResponse:
    """
    根据用户已有事实生成下一步信息补全清单。
    """
    case_data = request.model_dump()
    workflow = LegalWorkflowAnalyzer().analyze(case_data)
    missing_questions = []

    for item in workflow.jurisdiction.get("missing", []):
        missing_questions.append(f"请补充{item}。")
    for item in workflow.limitation.get("missing", []):
        missing_questions.append(f"请补充{item}。")
    if not case_data.get("facts") or len(case_data.get("facts", "")) < 50:
        missing_questions.append("请按时间顺序补充事件经过、沟通过程和当前诉求。")
    if not case_data.get("evidence"):
        missing_questions.append("请列出目前已有证据，例如劳动合同、工资流水、考勤、聊天记录。")

    return IntakeChecklistResponse(
        missing_questions=missing_questions,
        evidence_checklist=workflow.evidence_checklist,
        jurisdiction=workflow.jurisdiction,
        limitation=workflow.limitation,
    )


@router.get("/local-references", response_model=LocalReferenceResponse)
async def local_references(
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=10),
) -> LocalReferenceResponse:
    """查询重庆本地案例、指导意见和公开资料摘要。"""
    return LocalReferenceResponse(
        query=query,
        references=_format_local_references(query, limit),
    )


@router.post("/workup", response_model=CaseWorkupResponse)
@traceable_case("arbitration.workup")
async def case_workup(request: CaseAnalysisRequest) -> CaseWorkupResponse:
    """
    产品化综合研判：一次返回分析、补证、成本、成功率、本地参考和建议文书。
    """
    import asyncio

    pipeline = PipelineTracker()
    analysis = await _analyze_case_local(request)
    pipeline.record(
        "case_analysis",
        summary=f"{analysis.case_type} / {analysis.risk_level}",
        warnings=analysis.warnings or [],
    )
    intake = await intake_checklist(IntakeChecklistRequest(
        case_type=request.case_type,
        facts=request.facts,
        evidence=request.evidence,
        applicant_info=request.applicant_info,
    ))
    pipeline.record(
        "intake_checklist",
        summary=f"missing={len(intake.missing_questions or [])}",
        warnings=intake.missing_questions[:3],
    )

    # Parallelize independent calls
    analyzer = ArbitrationAnalyzer()
    case_dump = request.model_dump()
    query = f"{request.case_type} {request.facts}"

    async def _get_cost():
        return await analyzer.estimate_cost(case_dump)

    async def _get_prediction():
        return await analyzer.predict_success_rate(case_dump)

    async def _get_references():
        return _format_local_references(query, 5)

    cost_estimate, prediction, references = await asyncio.gather(
        _get_cost(), _get_prediction(), _get_references()
    )

    cost = ArbitrationCostEstimate(
        **cost_estimate,
        cost_estimate=cost_estimate["total_cost"],
        explanation="劳动争议仲裁不收费；这里主要估算律师费、复印交通等准备成本。",
    )
    pipeline.record("cost_estimate", summary=f"total={cost.total_cost}")
    success_prediction = SuccessRatePrediction(
        success_probability=prediction["success_probability"],
        probability_value=prediction["probability_value"],
        confidence=prediction["confidence"],
        key_factors=prediction["key_factors"],
        success_rate=prediction["success_probability"],
        explanation="预测值基于证据质量、证据数量和劳动者背景等规则因子，不能替代仲裁委最终裁判。",
    )
    pipeline.record(
        "success_prediction",
        summary=f"{success_prediction.success_probability}/{success_prediction.probability_value}",
        warnings=success_prediction.key_factors,
    )
    pipeline.record("local_references", summary=f"count={len(references)}")
    merged_missing = list(dict.fromkeys(
        [*(analysis.missing_info or []), *(intake.missing_questions or [])]
    ))
    merged_intake = IntakeChecklistResponse(
        missing_questions=merged_missing,
        evidence_checklist=intake.evidence_checklist,
        jurisdiction=intake.jurisdiction,
        limitation=intake.limitation,
    )
    workflow_stage = "补充事实和证据" if merged_missing or analysis.warnings else "可准备提交仲裁材料"
    suggested_documents = _suggest_document_types_from_claim_names(
        " ".join(item.get("name", "") for item in analysis.claim_items or [])
    )
    pipeline.record("final_assembly", summary=workflow_stage, warnings=merged_missing[:3])
    return CaseWorkupResponse(
        analysis=analysis,
        intake=merged_intake,
        cost=cost,
        success_prediction=success_prediction,
        local_references=references,
        suggested_documents=suggested_documents,
        workflow_stage=workflow_stage,
        service_recommendation=_build_service_recommendation(request, analysis, merged_intake, success_prediction),
        pipeline_status=pipeline.steps,
    )


# 添加案例查询接口（如果需要）
@router.get("/cases")
async def get_case_examples() -> Dict[str, Any]:
    """
    获取重庆地区劳动仲裁案例示例
    
    Returns:
        案例列表
    """
    try:
        # 这里可以连接到实际的案例数据库
        # 为了演示，返回一些示例数据
        sample_cases = [
            {
                "id": "CQ2023001",
                "title": "加班费争议案",
                "type": "加班费纠纷",
                "result": "支持申请人",
                "key_points": ["加班事实清楚", "公司未支付加班费", "适用《劳动法》第44条"]
            },
            {
                "id": "CQ2023002",
                "title": "违法解除劳动合同案",
                "type": "解除劳动合同争议",
                "result": "支持申请人",
                "key_points": ["解除程序违法", "未支付经济补偿金", "适用《劳动合同法》第48条"]
            },
            {
                "id": "CQ2023003",
                "title": "社保缴费争议案",
                "type": "社保缴费纠纷",
                "result": "部分支持申请人",
                "key_points": ["公司未缴社保", "申请人已离职", "适用《社会保险法》"]
            }
        ]
        
        return {"cases": sample_cases}
        
    except Exception:
        logger.exception("获取案例失败")
        raise HTTPException(status_code=500, detail="获取案例失败，请稍后重试。")
