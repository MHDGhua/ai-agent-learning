#!/usr/bin/env python3
"""
劳动仲裁分析服务
提供案件分析、风险评估、成本估算和成功率预测等功能
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, is_dataclass
from enum import Enum
import json
from datetime import datetime

from app.services.llm_client import LLMClient
from app.services.rag_retriever import retrieve_context
from app.services.chongqing_calculator import ChongqingLaborCalculator
from app.services.legal_workflow import LegalWorkflowAnalyzer
from app.services.chongqing_precedent import ChongqingPrecedentAdvisor
from app.agents.coordinator import CoordinatorAgent
from app.utils.json_helpers import safe_json_loads
from app.utils.parsers import parse_risk_level, parse_success_probability


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"


class SuccessProbability(str, Enum):
    """成功率等级"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


@dataclass
class ArbitrationAnalysis:
    """仲裁分析结果数据类"""
    case_type: str
    risk_level: RiskLevel
    risk_factors: List[str]
    cost_estimate: Dict[str, float]
    success_probability: SuccessProbability
    probability_confidence: float
    legal_basis: List[str]
    case_similarity: List[Dict[str, Any]]
    recommendations: List[str]
    missing_info: Optional[List[str]] = None  # 缺失信息提示
    opposition_review: Dict[str, Any] = None
    jurisdiction: Optional[Dict[str, Any]] = None
    limitation: Optional[Dict[str, Any]] = None
    claim_items: Optional[List[Dict[str, Any]]] = None
    evidence_checklist: Optional[List[Dict[str, Any]]] = None
    action_plan: Optional[List[str]] = None
    negotiation_points: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    local_reference: Optional[Dict[str, Any]] = None


class ArbitrationAnalyzer:
    """
    劳动仲裁分析服务
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.calculator = ChongqingLaborCalculator()
        self.workflow_analyzer = LegalWorkflowAnalyzer()
        self.precedent_advisor = ChongqingPrecedentAdvisor()

    def _normalize_cost_estimate(self, value: Any) -> Dict[str, float]:
        base = {
            "arbitration_fee": 0.0,
            "lawyer_fee": 3000.0,
            "other_costs": 200.0,
        }
        if isinstance(value, dict):
            for key in base:
                try:
                    base[key] = round(float(value.get(key, base[key])), 2)
                except Exception:
                    continue
        base["total_cost"] = round(sum(base.values()), 2)
        return base

    def _ensure_list(self, value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

    def _build_case_similarity(self, context_data: List[str], local_reference: Dict[str, Any]) -> List[Dict[str, Any]]:
        similarity: List[Dict[str, Any]] = []
        for idx, item in enumerate(local_reference.get("guidance", [])[:3], start=1):
            similarity.append({
                "case_id": item.get("title", f"local_{idx}"),
                "similarities": [item.get("summary", "")] if item.get("summary") else [],
                "outcome": item.get("applicability") or item.get("result") or "本地参考",
            })
        if not similarity:
            for idx, item in enumerate(context_data[:2], start=1):
                similarity.append({
                    "case_id": f"context_{idx}",
                    "similarities": [item[:120]],
                    "outcome": "检索参考",
                })
        return similarity

    async def _build_rule_based_analysis(
        self,
        case_data: Dict[str, Any],
        workflow: Any,
        local_reference: Dict[str, Any],
        context_data: List[str],
    ) -> Dict[str, Any]:
        missing_info = self._detect_missing_info(case_data)
        cost_estimate = await self.estimate_cost(case_data)
        success_prediction = await self.predict_success_rate(case_data)
        warnings = list(workflow.warnings or [])
        risk_factors = list(dict.fromkeys(
            warnings
            + (missing_info or [])
            + [f"本地参考优先级: {local_reference.get('priority', 'unknown')}"]
        ))

        if workflow.limitation.get("status") == "possibly_expired" or len(missing_info or []) >= 3:
            risk_level = RiskLevel.HIGH
        elif warnings or missing_info:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        recommendations = self._merge_local_recommendations(
            (workflow.action_plan or []) + local_reference.get("reference_strategy", []),
            local_reference,
            workflow.action_plan,
        )

        return {
            "case_type": case_data.get("case_type", "未知"),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "cost_estimate": cost_estimate,
            "success_probability": parse_success_probability(
                success_prediction.get("success_probability"),
                SuccessProbability.MEDIUM,
            ),
            "probability_confidence": float(success_prediction.get("confidence", 0.5)),
            "legal_basis": workflow.legal_basis or [],
            "case_similarity": self._build_case_similarity(context_data, local_reference),
            "recommendations": recommendations,
            "missing_info": missing_info,
            "jurisdiction": workflow.jurisdiction,
            "limitation": workflow.limitation,
            "claim_items": workflow.claim_items,
            "evidence_checklist": workflow.evidence_checklist,
            "action_plan": workflow.action_plan,
            "negotiation_points": workflow.negotiation_points,
            "warnings": warnings,
            "local_reference": local_reference,
        }
    
    async def analyze_case(
        self,
        case_data: Dict[str, Any],
        coordinator: CoordinatorAgent = None
    ) -> ArbitrationAnalysis:
        """
        综合分析案件情况
        
        Args:
            case_data: 案件数据
            coordinator: 协调器Agent（可选，用于红蓝对抗）
            
        Returns:
            案件分析结果
        """
        # 1. 获取案件相关信息
        case_type = case_data.get('case_type', '未知')
        facts = case_data.get('facts', '')
        evidence = case_data.get('evidence', [])
        applicant_info = case_data.get('applicant_info', {})
        workflow = self.workflow_analyzer.analyze(case_data)
        local_reference = self.precedent_advisor.build_local_reference(case_data)
        
        # 2. 获取相关法律条文和案例
        context_data = retrieve_context(
            f"重庆劳动仲裁案件分析 {case_type}",
            top_k=5
        )
        local_context = [
            f"{item['title']}：{item['summary']}"
            for item in local_reference.get("guidance", [])
        ]
        context_data = local_context + context_data

        base_analysis = await self._build_rule_based_analysis(case_data, workflow, local_reference, context_data)

        # 3. 构造分析prompt
        prompt = (
            "你是重庆地区的劳动仲裁专家，请根据以下案件信息进行全面分析。\n\n"
            "案件信息:\n"
            f"案件类型: {case_type}\n"
            f"案件事实: {facts}\n"
            f"证据材料: {', '.join(evidence) if evidence else '无'}\n"
            f"申请人信息: {json.dumps(applicant_info, ensure_ascii=False)}\n\n"
            "要求:\n"
            "1. 分析案件的风险等级（低/中/高）\n"
            "2. 列出主要风险因素\n"
            "3. 估算仲裁成本（包括仲裁费、律师费等）\n"
            "4. 预测胜诉概率（高/中/低）及置信度\n"
            "5. 提供法律依据\n"
            "6. 推荐处理建议\n"
            "7. 如果有相似案例，请提供参考\n\n"
            "请以JSON格式返回分析结果，包含以下字段:\n"
            "{\n"
            "  \"case_type\": \"案件类型\",\n"
            "  \"risk_level\": \"风险等级\",\n"
            "  \"risk_factors\": [\"风险因素1\", \"风险因素2\"],\n"
            "  \"cost_estimate\": {\n"
            "    \"arbitration_fee\": 仲裁费,\n"
            "    \"lawyer_fee\": 律师费,\n"
            "    \"other_costs\": 其他费用\n"
            "  },\n"
            "  \"success_probability\": \"成功率等级\",\n"
            "  \"probability_confidence\": 0.0-1.0,\n"
            "  \"legal_basis\": [\"法律条文1\", \"法律条文2\"],\n"
            "  \"case_similarity\": [\n"
            "    {\n"
            "      \"case_id\": \"案例ID\",\n"
            "      \"similarities\": [\"相似点1\", \"相似点2\"],\n"
            "      \"outcome\": \"结果\"\n"
            "    }\n"
            "  ],\n"
            "  \"recommendations\": [\"建议1\", \"建议2\"]\n"
            "}\n"
        )

        parsed_data: Dict[str, Any] = {}
        try:
            response = await self.llm_client.generate_draft(prompt, "audit", context_data)
            try:
                parsed_data = safe_json_loads(response)
            except Exception:
                parsed_data = {}
        except Exception as e:
            parsed_data = {}

        merged = dict(base_analysis)
        for key, value in parsed_data.items():
            if value in (None, "", [], {}):
                continue
            merged[key] = value

        missing_info = merged.get("missing_info") or self._detect_missing_info(case_data)
        cost_estimate = self._normalize_cost_estimate(merged.get("cost_estimate"))
        probability_confidence = merged.get("probability_confidence", base_analysis["probability_confidence"])
        try:
            probability_confidence = max(0.0, min(1.0, float(probability_confidence)))
        except Exception:
            probability_confidence = base_analysis["probability_confidence"]

        analysis = ArbitrationAnalysis(
            case_type=str(merged.get("case_type", case_type)),
            risk_level=parse_risk_level(merged.get("risk_level"), base_analysis["risk_level"]),
            risk_factors=list(dict.fromkeys(self._ensure_list(merged.get("risk_factors") or base_analysis["risk_factors"]))),
            cost_estimate=cost_estimate,
            success_probability=parse_success_probability(
                merged.get("success_probability"),
                base_analysis["success_probability"],
            ),
            probability_confidence=probability_confidence,
            legal_basis=self._ensure_list(merged.get("legal_basis") or base_analysis["legal_basis"]),
            case_similarity=self._ensure_list(merged.get("case_similarity") or base_analysis["case_similarity"]),
            recommendations=self._merge_local_recommendations(
                self._ensure_list(merged.get("recommendations", [])),
                local_reference,
                workflow.action_plan,
            ),
            missing_info=missing_info if missing_info else None,
            jurisdiction=merged.get("jurisdiction") or workflow.jurisdiction,
            limitation=merged.get("limitation") or workflow.limitation,
            claim_items=self._ensure_list(merged.get("claim_items") or workflow.claim_items),
            evidence_checklist=self._ensure_list(merged.get("evidence_checklist") or workflow.evidence_checklist),
            action_plan=self._ensure_list(merged.get("action_plan") or workflow.action_plan),
            negotiation_points=self._ensure_list(merged.get("negotiation_points") or workflow.negotiation_points),
            warnings=self._ensure_list(merged.get("warnings") or workflow.warnings),
            local_reference=merged.get("local_reference") or local_reference,
        )

        if coordinator:
            try:
                opposition_review = await coordinator.conduct_opposition_review(case_data, merged)
                if is_dataclass(opposition_review):
                    opposition_review = asdict(opposition_review)
                analysis.opposition_review = opposition_review
            except Exception:
                analysis.opposition_review = {}
        return analysis
    
    def _detect_missing_info(self, case_data: Dict[str, Any]) -> Optional[List[str]]:
        """
        检测案件信息中缺失的关键内容
        
        Args:
            case_data: 案件数据
            
        Returns:
            缺失信息列表，如果没有缺失则返回 None
        """
        missing_info = []
        
        # 检查事实描述是否足够详细
        facts = case_data.get('facts', '')
        if not facts or len(facts) < 50:
            missing_info.append("• 请详细描述事件经过，包括时间、地点、涉及人员等")
        
        # 检查用人单位信息
        applicant_info = case_data.get('applicant_info', {})
        if not applicant_info.get('employer_name'):
            missing_info.append("• 请提供用人单位名称")
        
        # 检查入职时间
        if not applicant_info.get('start_date'):
            missing_info.append("• 请提供入职时间")
        
        # 检查工资水平
        if not case_data.get('salary') and not applicant_info.get('salary'):
            missing_info.append("• 请提供您的工资水平")
        
        # 检查证据材料
        evidence = case_data.get('evidence', [])
        if not evidence or len(evidence) == 0:
            missing_info.append("• 请说明您目前掌握的证据材料（如劳动合同、工资条、聊天记录等）")
        
        return missing_info if missing_info else None
    
    def _create_default_analysis(self, case_data: Dict[str, Any]) -> ArbitrationAnalysis:
        """
        创建默认分析结果
        """
        case_type = case_data.get('case_type', '未知')
        missing_info = self._detect_missing_info(case_data)
        workflow = self.workflow_analyzer.analyze(case_data)
        local_reference = self.precedent_advisor.build_local_reference(case_data)

        cost_estimate = {
            "arbitration_fee": 0.0,
            "lawyer_fee": 3000.0,
            "other_costs": 200.0,
            "total_cost": 3200.0,
        }
        risk_level = RiskLevel.HIGH if workflow.warnings else RiskLevel.MEDIUM
        success_probability = SuccessProbability.MEDIUM

        return ArbitrationAnalysis(
            case_type=case_type,
            risk_level=risk_level,
            risk_factors=list(dict.fromkeys((workflow.warnings or []) + (missing_info or []) + ["需要更多证据支持"])),
            cost_estimate=cost_estimate,
            success_probability=success_probability,
            probability_confidence=0.55 if not workflow.warnings else 0.45,
            legal_basis=workflow.legal_basis,
            case_similarity=self._build_case_similarity([], local_reference),
            recommendations=self._merge_local_recommendations([], local_reference, workflow.action_plan),
            missing_info=missing_info,
            jurisdiction=workflow.jurisdiction,
            limitation=workflow.limitation,
            claim_items=workflow.claim_items,
            evidence_checklist=workflow.evidence_checklist,
            action_plan=workflow.action_plan,
            negotiation_points=workflow.negotiation_points,
            warnings=workflow.warnings,
            opposition_review={},
            local_reference=local_reference,
        )

    def _merge_local_recommendations(
        self,
        base_recommendations: List[str],
        local_reference: Dict[str, Any],
        action_plan: List[str],
    ) -> List[str]:
        merged = []
        for item in local_reference.get("reference_strategy", []):
            if item not in merged:
                merged.append(item)
        for item in action_plan:
            if item not in merged:
                merged.append(item)
        for item in base_recommendations:
            if item not in merged:
                merged.append(item)
        return merged[:8]
    
    async def estimate_cost(
        self, 
        case_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        估算仲裁成本
        
        Args:
            case_data: 案件数据
            
        Returns:
            成本估算结果
        """
        # 基于案件类型和具体情况估算成本
        case_type = case_data.get('case_type', '')
        applicant_info = case_data.get("applicant_info") or {}
        salary = case_data.get('salary') or applicant_info.get("salary") or 0
        years = case_data.get('years') or applicant_info.get("years") or 0
        
        # 劳动争议仲裁不收费；这里保留字段是为了前端展示统一。
        arbitration_fee = 0.0
        
        # 律师费用（根据案件复杂程度）
        lawyer_fee = 3000.0  # 基础律师费
        
        # 其他费用
        other_costs = 200.0  # 交通、复印等费用
        
        # 根据案件类型调整费用
        if '赔偿' in case_type or '补偿' in case_type:
            # 赔偿类案件通常费用较高
            arbitration_fee *= 1.5
            lawyer_fee *= 2.0
        elif '合同' in case_type or '解除' in case_type:
            # 合同类案件费用适中
            arbitration_fee *= 1.2
            lawyer_fee *= 1.5
        
        # 根据工作年限调整费用
        if years > 5:
            lawyer_fee *= 1.3
        
        return {
            "arbitration_fee": round(arbitration_fee, 2),
            "lawyer_fee": round(lawyer_fee, 2),
            "other_costs": round(other_costs, 2),
            "total_cost": round(arbitration_fee + lawyer_fee + other_costs, 2)
        }
    
    async def predict_success_rate(
        self, 
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        预测仲裁成功率
        
        Args:
            case_data: 案件数据
            
        Returns:
            成功率预测结果
        """
        # 获取案件特征
        case_type = case_data.get('case_type', '')
        evidence_quality = case_data.get('evidence_quality', '一般')
        evidence_count = len(case_data.get('evidence', []))
        applicant_background = case_data.get('applicant_background', '普通员工')
        
        # 基于特征计算成功率
        base_probability = 0.5  # 基础成功率
        
        # 根据证据质量调整
        if evidence_quality == '优秀':
            base_probability += 0.2
        elif evidence_quality == '良好':
            base_probability += 0.1
        elif evidence_quality == '一般':
            base_probability -= 0.05
        elif evidence_quality == '较差':
            base_probability -= 0.2
        
        # 根据证据数量调整
        if evidence_count >= 5:
            base_probability += 0.15
        elif evidence_count >= 3:
            base_probability += 0.05
        elif evidence_count <= 1:
            base_probability -= 0.15
        
        # 根据申请人背景调整
        if applicant_background == '管理层':
            base_probability -= 0.1
        elif applicant_background == '特殊群体':
            base_probability += 0.1
        
        # 确保概率在合理范围内
        success_probability = max(0.1, min(0.9, base_probability))
        
        # 确定成功率等级
        if success_probability >= 0.7:
            probability_level = SuccessProbability.HIGH
        elif success_probability >= 0.4:
            probability_level = SuccessProbability.MEDIUM
        else:
            probability_level = SuccessProbability.LOW
        
        return {
            "success_probability": probability_level.value,
            "probability_value": round(success_probability, 3),
            "confidence": round(min(0.9, success_probability + 0.1), 3),
            "key_factors": [
                f"证据质量: {evidence_quality}",
                f"证据数量: {evidence_count}份",
                f"申请人背景: {applicant_background}"
            ]
        }


# 创建全局实例
arbitration_analyzer = ArbitrationAnalyzer()
