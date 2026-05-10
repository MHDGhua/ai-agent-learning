#!/usr/bin/env python3
"""
红蓝对抗律师Agent
实现红蓝双方律师在仲裁分析中的对抗审查机制
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import json

from app.agents.base import BaseAgent, AgentCapability
from app.services.llm_client import LLMClient
from app.services.rag_retriever import retrieve_context
from app.services.legal_workflow import LegalWorkflowAnalyzer


class LawyerRole(str, Enum):
    """律师角色枚举"""
    RED = "red"      # 红方律师（申请人立场）
    BLUE = "blue"    # 蓝方律师（被申请人立场）


class VulnerabilityType(str, Enum):
    """漏洞类型枚举"""
    LEGAL_BASIS = "legal_basis"          # 法律依据问题
    EVIDENCE_GAP = "evidence_gap"        # 证据不足
    LOGIC_FLAW = "logic_flaw"            # 逻辑漏洞
    CASE_REFERENCE = "case_reference"    # 案例引用问题
    ARGUMENT_STRUCTURE = "argument_structure"  # 论证结构问题


@dataclass
class VulnerabilityReport:
    """漏洞报告数据类"""
    vulnerability_type: VulnerabilityType
    description: str
    severity: str  # low/medium/high
    suggested_fix: str
    confidence: float  # 0.0-1.0


@dataclass
class OppositionReviewResult:
    """对抗审查结果数据类"""
    red_lawyer_analysis: Dict[str, Any]
    blue_lawyer_analysis: Dict[str, Any]
    vulnerabilities_found: List[VulnerabilityReport]
    improvement_suggestions: List[str]
    final_recommendation: str
    success_probability_improvement: float


def build_agent_result(
    *,
    agent_id: str,
    agent_name: str,
    status: str,
    summary: str,
    confidence: float,
    warnings: Optional[List[str]] = None,
    output: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "agent_id": agent_id,
        "agent_name": agent_name,
        "status": status,
        "summary": summary,
        "confidence": round(max(0.0, min(1.0, confidence)), 3),
        "warnings": warnings or [],
        "output": output or {},
    }


class RedBlueLawyerAgent(BaseAgent):
    """
    红蓝对抗律师Agent
    负责在仲裁分析中进行红蓝双方的对抗审查
    """
    
    def __init__(self, llm_client: LLMClient, knowledge_base: Any, role: LawyerRole):
        """
        初始化红蓝律师Agent
        
        Args:
            llm_client: LLM客户端
            knowledge_base: 知识库
            role: 律师角色（红方/蓝方）
        """
        super().__init__(
            agent_id=f"{'red' if role == LawyerRole.RED else 'blue'}_lawyer",
            agent_name=f"{'红方' if role == LawyerRole.RED else '蓝方'}律师",
            capability=AgentCapability(
                domain="opposition_review",
                expertise_level=8,
                supported_tasks=["opposition_review"],
                required_knowledge=["labor_law", "evidence_rules"],
            ),
            llm_client=llm_client,
            knowledge_base=knowledge_base,
        )
        self.role = role
        self.name = f"{'红方' if role == LawyerRole.RED else '蓝方'}律师"

    async def analyze(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.analyze_case_opposition(case_data, {})

    async def collaborate(
        self,
        other_agents: List[BaseAgent],
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self.analyze(case_data)
    
    async def analyze_case_opposition(
        self, 
        case_data: Dict[str, Any],
        original_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        进行对抗性分析
        
        Args:
            case_data: 案件数据
            original_analysis: 原始分析结果
            
        Returns:
            对抗性分析结果
        """
        # 根据角色生成不同的分析视角，先生成确定性结果，再尝试 LLM 增强
        if self.role == LawyerRole.RED:
            return await self._analyze_from_applicant_perspective(case_data, original_analysis)
        return await self._analyze_from_respondent_perspective(case_data, original_analysis)
    
    async def _analyze_from_applicant_perspective(
        self, 
        case_data: Dict[str, Any], 
        original_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        从申请人角度进行分析（红方）
        """
        # 获取相关法律条文和案例
        context_data = retrieve_context(
            f"重庆劳动仲裁申请人立场分析 {case_data.get('case_type', '')}", 
            top_k=5
        )
        
        fallback = self._build_fallback_analysis(case_data, original_analysis, "red")

        prompt = (
            "你是重庆地区的劳动仲裁红方律师，代表申请人立场。\n\n"
            "案件信息:\n"
            f"案件类型: {case_data.get('case_type', '未知')}\n"
            f"案件事实: {case_data.get('facts', '无')}\n"
            f"证据材料: {', '.join(case_data.get('evidence', [])) if case_data.get('evidence') else '无'}\n\n"
            "原始分析结果:\n"
            f"{json.dumps(original_analysis, ensure_ascii=False, indent=2)}\n\n"
            "你的任务:\n"
            "1. 从申请人角度审视原始分析\n"
            "2. 找出可能存在的漏洞和不足\n"
            "3. 提供针对性的改进建议\n"
            "4. 强调有利于申请人的观点\n"
            "5. 保持专业和客观\n\n"
            "请以JSON格式返回分析结果，包含以下字段:\n"
            "{\n"
            "  \"role\": \"红方律师\",\n"
            "  \"perspective\": \"申请人立场\",\n"
            "  \"key_arguments\": [\"关键论点1\", \"关键论点2\"],\n"
            "  \"strengths\": [\"优势1\", \"优势2\"],\n"
            "  \"weaknesses\": [\"劣势1\", \"劣势2\"],\n"
            "  \"improvement_suggestions\": [\"改进建议1\", \"改进建议2\"]\n"
            "}\n"
        )
        
        if not self.llm_client:
            return fallback
        try:
            response = await self.llm_client.generate_draft(prompt, "audit", context_data)
            parsed = self._parse_json_response(response)
            if parsed:
                return self._merge_analysis(fallback, parsed)
            return fallback
        except Exception:
            return fallback
    
    async def _analyze_from_respondent_perspective(
        self, 
        case_data: Dict[str, Any], 
        original_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        从被申请人角度进行分析（蓝方）
        """
        # 获取相关法律条文和案例
        context_data = retrieve_context(
            f"重庆劳动仲裁被申请人立场分析 {case_data.get('case_type', '')}", 
            top_k=5
        )
        
        fallback = self._build_fallback_analysis(case_data, original_analysis, "blue")

        prompt = (
            "你是重庆地区的劳动仲裁蓝方律师，代表被申请人立场。\n\n"
            "案件信息:\n"
            f"案件类型: {case_data.get('case_type', '未知')}\n"
            f"案件事实: {case_data.get('facts', '无')}\n"
            f"证据材料: {', '.join(case_data.get('evidence', [])) if case_data.get('evidence') else '无'}\n\n"
            "原始分析结果:\n"
            f"{json.dumps(original_analysis, ensure_ascii=False, indent=2)}\n\n"
            "你的任务:\n"
            "1. 从被申请人角度审视原始分析\n"
            "2. 找出可能存在的漏洞和不足\n"
            "3. 提供针对性的反驳意见\n"
            "4. 强调有利于被申请人的观点\n"
            "5. 保持专业和客观\n\n"
            "请以JSON格式返回分析结果，包含以下字段:\n"
            "{\n"
            "  \"role\": \"蓝方律师\",\n"
            "  \"perspective\": \"被申请人立场\",\n"
            "  \"key_arguments\": [\"关键论点1\", \"关键论点2\"],\n"
            "  \"strengths\": [\"优势1\", \"优势2\"],\n"
            "  \"weaknesses\": [\"劣势1\", \"劣势2\"],\n"
            "  \"improvement_suggestions\": [\"改进建议1\", \"改进建议2\"]\n"
            "}\n"
        )
        
        if not self.llm_client:
            return fallback
        try:
            response = await self.llm_client.generate_draft(prompt, "audit", context_data)
            parsed = self._parse_json_response(response)
            if parsed:
                return self._merge_analysis(fallback, parsed)
            return fallback
        except Exception:
            return fallback

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        raw = (response or "").strip()
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
        except Exception:
            start = raw.find("{")
            end = raw.rfind("}")
            if start < 0 or end <= start:
                return {}
            try:
                parsed = json.loads(raw[start : end + 1])
            except Exception:
                return {}
        return parsed if isinstance(parsed, dict) else {}

    def _merge_analysis(self, fallback: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(fallback)
        for key, value in parsed.items():
            if value in (None, "", [], {}):
                continue
            merged[key] = value
        return merged

    def _build_fallback_analysis(
        self,
        case_data: Dict[str, Any],
        original_analysis: Dict[str, Any],
        role: str,
    ) -> Dict[str, Any]:
        workflow = LegalWorkflowAnalyzer().analyze(case_data)
        facts = f"{case_data.get('case_type', '')}{case_data.get('facts', '')}"
        claim_items = workflow.claim_items or []
        legal_basis = workflow.legal_basis or []
        missing_info = original_analysis.get("missing_info") or []
        risk_flags = list(dict.fromkeys((original_analysis.get("risk_factors") or []) + workflow.warnings))
        if role == "red":
            key_arguments = self._build_red_arguments(case_data, workflow, claim_items)
            strengths = [
                "有利事实应围绕劳动关系、工资支付和解除程序展开。",
                "先把证据链闭合，再强调本地规则和请求金额。",
            ]
            weaknesses = self._build_common_weaknesses(missing_info, legal_basis, workflow.warnings)
            improvement = [
                "补充时间线、工资流水、考勤和解除通知。",
                "把仲裁请求拆分为事实、金额和证据三部分。",
            ]
            perspective = "申请人立场"
            role_name = "红方律师"
        else:
            key_arguments = self._build_blue_arguments(case_data, workflow, claim_items)
            strengths = [
                "重点核查申请请求是否超过证据支撑范围。",
                "优先利用时效、管辖和证据缺口进行防守。",
            ]
            weaknesses = self._build_common_weaknesses(missing_info, legal_basis, workflow.warnings)
            improvement = [
                "逐项核对仲裁请求对应证据和金额来源。",
                "先锁定时效与管辖，再展开实体抗辩。",
            ]
            perspective = "被申请人立场"
            role_name = "蓝方律师"

        return {
            "role": role_name,
            "perspective": perspective,
            "agent_result": build_agent_result(
                agent_id=self.agent_id,
                agent_name=role_name,
                status="ok",
                summary=f"{role_name}完成{perspective}审查。",
                confidence=0.82 if risk_flags else 0.76,
                warnings=risk_flags[:3],
            ),
            "summary": f"{role_name}已完成规则化对抗审查，当前关注点是{'；'.join(risk_flags[:2]) if risk_flags else '证据和法律依据对齐'}。",
            "key_arguments": key_arguments,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_suggestions": improvement,
            "risk_flags": risk_flags,
            "legal_basis": legal_basis,
            "workflow": workflow.to_dict(),
        }

    def _build_red_arguments(
        self,
        case_data: Dict[str, Any],
        workflow,
        claim_items: List[Dict[str, Any]],
    ) -> List[str]:
        args = ["申请人应优先证明劳动关系和争议事实链条完整。"]
        if workflow.jurisdiction.get("likely_chongqing_jurisdiction"):
            args.append("重庆管辖要素较明确，可尽快进入受理准备。")
        if workflow.limitation.get("status") == "within_period":
            args.append("时效风险相对可控，适合尽快提交申请。")
        for item in claim_items[:2]:
            args.append(f"围绕{item['name']}准备金额和证据对应关系。")
        if any(keyword in f"{case_data.get('case_type', '')}{case_data.get('facts', '')}" for keyword in ["工伤", "受伤"]):
            args.append("工伤案件应补齐认定和鉴定材料。")
        return list(dict.fromkeys(args))[:5]

    def _build_blue_arguments(
        self,
        case_data: Dict[str, Any],
        workflow,
        claim_items: List[Dict[str, Any]],
    ) -> List[str]:
        args = ["被申请人应优先核查事实、金额和程序三条线。"]
        if workflow.jurisdiction.get("missing"):
            args.append("管辖要素缺失时，可先要求申请人补充。")
        if workflow.limitation.get("status") == "possibly_expired":
            args.append("时效可能已过，适合作为首要抗辩点。")
        if not claim_items:
            args.append("诉求类型不明确时，应先要求明确请求事项。")
        if not case_data.get("evidence"):
            args.append("证据缺口较大，可重点争取压缩申请人举证空间。")
        return list(dict.fromkeys(args))[:5]

    def _build_common_weaknesses(
        self,
        missing_info: List[str],
        legal_basis: List[str],
        warnings: List[str],
    ) -> List[str]:
        weaknesses = []
        if missing_info:
            weaknesses.append("案件信息仍有缺失，需先补齐关键事实。")
        if not legal_basis:
            weaknesses.append("法律依据不足，需核对适用条文。")
        if warnings:
            weaknesses.append(warnings[0])
        return weaknesses or ["当前论证尚需补强证据和法律依据。"]


class OppositionReviewerAgent(BaseAgent):
    """
    对抗审查Agent
    负责协调红蓝双方律师的对抗分析，识别漏洞并提供改进建议
    """
    
    def __init__(self, llm_client: LLMClient, knowledge_base: Any):
        """
        初始化对抗审查Agent
        
        Args:
            llm_client: LLM客户端
            knowledge_base: 知识库
        """
        super().__init__(
            agent_id="opposition_reviewer_001",
            agent_name="对抗审查员",
            capability=AgentCapability(
                domain="opposition_review",
                expertise_level=8,
                supported_tasks=["opposition_review"],
                required_knowledge=["labor_law", "evidence_rules"],
            ),
            llm_client=llm_client,
            knowledge_base=knowledge_base,
        )
        self.name = "对抗审查员"

    async def analyze(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.conduct_opposition_review(case_data, {})
        return {
            "red_lawyer_analysis": result.red_lawyer_analysis,
            "blue_lawyer_analysis": result.blue_lawyer_analysis,
            "vulnerabilities_found": [v.__dict__ for v in result.vulnerabilities_found],
            "improvement_suggestions": result.improvement_suggestions,
            "final_recommendation": result.final_recommendation,
            "success_probability_improvement": result.success_probability_improvement,
        }

    async def collaborate(
        self,
        other_agents: List[BaseAgent],
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self.analyze(case_data)
    
    async def conduct_opposition_review(
        self, 
        case_data: Dict[str, Any],
        original_analysis: Dict[str, Any]
    ) -> OppositionReviewResult:
        """
        进行对抗审查
        
        Args:
            case_data: 案件数据
            original_analysis: 原始分析结果
            
        Returns:
            对抗审查结果
        """
        # 创建红蓝双方律师
        red_lawyer = RedBlueLawyerAgent(self.llm_client, self.knowledge_base, LawyerRole.RED)
        blue_lawyer = RedBlueLawyerAgent(self.llm_client, self.knowledge_base, LawyerRole.BLUE)
        
        # 并行执行双方分析
        red_analysis_task = red_lawyer.analyze_case_opposition(case_data, original_analysis)
        blue_analysis_task = blue_lawyer.analyze_case_opposition(case_data, original_analysis)
        
        # 等待两个分析完成
        red_analysis, blue_analysis = await asyncio.gather(
            red_analysis_task, 
            blue_analysis_task,
            return_exceptions=True
        )
        
        # 处理异常情况
        if isinstance(red_analysis, Exception):
            red_analysis = {
                "role": "红方律师",
                "perspective": "申请人立场",
                "key_arguments": [],
                "strengths": [],
                "weaknesses": ["分析失败"],
                "improvement_suggestions": []
            }
        
        if isinstance(blue_analysis, Exception):
            blue_analysis = {
                "role": "蓝方律师",
                "perspective": "被申请人立场",
                "key_arguments": [],
                "strengths": [],
                "weaknesses": ["分析失败"],
                "improvement_suggestions": []
            }
        
        # 识别漏洞
        vulnerabilities = await self._identify_vulnerabilities(
            case_data, 
            original_analysis, 
            red_analysis, 
            blue_analysis
        )
        
        # 生成改进建议
        improvement_suggestions = await self._generate_improvements(
            case_data, 
            original_analysis, 
            red_analysis, 
            blue_analysis, 
            vulnerabilities
        )
        
        # 生成最终建议
        final_recommendation = await self._generate_final_recommendation(
            case_data,
            original_analysis,
            red_analysis,
            blue_analysis,
            vulnerabilities,
            improvement_suggestions
        )
        
        # 计算成功率提升
        success_probability_improvement = await self._calculate_success_probability_improvement(
            original_analysis,
            red_analysis,
            blue_analysis,
            vulnerabilities
        )
        
        return OppositionReviewResult(
            red_lawyer_analysis=self._ensure_agent_result(red_analysis, "red_lawyer", "红方律师"),
            blue_lawyer_analysis=self._ensure_agent_result(blue_analysis, "blue_lawyer", "蓝方律师"),
            vulnerabilities_found=vulnerabilities,
            improvement_suggestions=improvement_suggestions,
            final_recommendation=final_recommendation,
            success_probability_improvement=success_probability_improvement
        )

    def _ensure_agent_result(self, analysis: Dict[str, Any], agent_id: str, agent_name: str) -> Dict[str, Any]:
        if analysis.get("agent_result"):
            return analysis
        warnings = analysis.get("weaknesses") or analysis.get("risk_flags") or []
        analysis["agent_result"] = build_agent_result(
            agent_id=agent_id,
            agent_name=analysis.get("role") or agent_name,
            status="ok" if "分析失败" not in warnings else "error",
            summary=analysis.get("summary") or f"{agent_name}完成审查。",
            confidence=0.72,
            warnings=warnings[:3],
        )
        return analysis
    
    async def _identify_vulnerabilities(
        self,
        case_data: Dict[str, Any],
        original_analysis: Dict[str, Any],
        red_analysis: Dict[str, Any],
        blue_analysis: Dict[str, Any]
    ) -> List[VulnerabilityReport]:
        """识别潜在漏洞，规则优先。"""
        workflow = LegalWorkflowAnalyzer().analyze(case_data)
        vulnerabilities: List[VulnerabilityReport] = []

        if not original_analysis.get("legal_basis"):
            vulnerabilities.append(VulnerabilityReport(
                vulnerability_type=VulnerabilityType.LEGAL_BASIS,
                description="法律依据引用偏少，论证支撑不够稳定",
                severity="medium",
                suggested_fix="补充适用条文和本地参考依据",
                confidence=0.85,
            ))
        if not case_data.get("evidence"):
            vulnerabilities.append(VulnerabilityReport(
                vulnerability_type=VulnerabilityType.EVIDENCE_GAP,
                description="证据目录为空，关键事实缺少支撑",
                severity="high",
                suggested_fix="补齐劳动合同、工资流水、考勤和沟通记录",
                confidence=0.95,
            ))
        if workflow.limitation.get("status") == "possibly_expired":
            vulnerabilities.append(VulnerabilityReport(
                vulnerability_type=VulnerabilityType.LOGIC_FLAW,
                description="仲裁时效可能已过，但原始分析未优先提示",
                severity="high",
                suggested_fix="先核查中断、中止和特殊时效规则",
                confidence=0.9,
            ))
        if workflow.jurisdiction.get("missing"):
            vulnerabilities.append(VulnerabilityReport(
                vulnerability_type=VulnerabilityType.ARGUMENT_STRUCTURE,
                description="管辖要素未补齐，论证结构可能过早定论",
                severity="medium",
                suggested_fix="补齐工作地、合同履行地和单位住所地信息",
                confidence=0.82,
            ))
        if not original_analysis.get("case_similarity"):
            vulnerabilities.append(VulnerabilityReport(
                vulnerability_type=VulnerabilityType.CASE_REFERENCE,
                description="缺少相似案例或本地参考，类案支撑偏弱",
                severity="medium",
                suggested_fix="补充重庆本地典型案例和指导意见参考",
                confidence=0.7,
            ))

        if not vulnerabilities:
            vulnerabilities.append(VulnerabilityReport(
                vulnerability_type=VulnerabilityType.LEGAL_BASIS,
                description="当前结构较完整，但仍需确认材料与结论一一对应",
                severity="low",
                suggested_fix="继续按证据目录复核每项请求的证明目的",
                confidence=0.6,
            ))
        return vulnerabilities
    
    async def _generate_improvements(
        self,
        case_data: Dict[str, Any],
        original_analysis: Dict[str, Any],
        red_analysis: Dict[str, Any],
        blue_analysis: Dict[str, Any],
        vulnerabilities: List[VulnerabilityReport]
    ) -> List[str]:
        """生成改进建议。"""
        improvements: List[str] = []
        for vuln in vulnerabilities:
            if vuln.suggested_fix not in improvements:
                improvements.append(vuln.suggested_fix)
        if red_analysis.get("improvement_suggestions"):
            for item in red_analysis["improvement_suggestions"]:
                if item not in improvements:
                    improvements.append(item)
        if blue_analysis.get("improvement_suggestions"):
            for item in blue_analysis["improvement_suggestions"]:
                if item not in improvements:
                    improvements.append(item)
        if not improvements:
            improvements = ["补充相关法律条文引用", "完善证据材料", "加强论证逻辑"]
        return improvements[:6]
    
    async def _generate_final_recommendation(
        self,
        case_data: Dict[str, Any],
        original_analysis: Dict[str, Any],
        red_analysis: Dict[str, Any],
        blue_analysis: Dict[str, Any],
        vulnerabilities: List[VulnerabilityReport],
        improvements: List[str]
    ) -> str:
        """生成最终建议。"""
        case_type = case_data.get("case_type", "劳动纠纷")
        major_points = "；".join([v.description for v in vulnerabilities[:3]]) if vulnerabilities else "当前结构较完整"
        improvement_points = "；".join(improvements[:3]) if improvements else "补充证据并复核逻辑"
        return (
            f"{case_type}案件建议按红蓝对抗结果优先补齐证据、时效和管辖要素；"
            f"当前主要风险是{major_points}；"
            f"优先改进方向：{improvement_points}。"
        )
    
    async def _calculate_success_probability_improvement(
        self,
        original_analysis: Dict[str, Any],
        red_analysis: Dict[str, Any],
        blue_analysis: Dict[str, Any],
        vulnerabilities: List[VulnerabilityReport]
    ) -> float:
        """
        计算成功率提升幅度
        """
        # 基于漏洞数量和严重程度计算提升幅度
        high_severity_vulns = sum(1 for v in vulnerabilities if v.severity == "high")
        medium_severity_vulns = sum(1 for v in vulnerabilities if v.severity == "medium")
        
        # 每个高危漏洞减少0.15的成功率，每个中危漏洞减少0.05的成功率
        reduction = high_severity_vulns * 0.15 + medium_severity_vulns * 0.05
        
        # 基于改进效果，成功率提升幅度为减少的百分比的70%
        improvement = reduction * 0.7
        
        # 确保提升幅度在合理范围内（0-0.3）
        return max(0.0, min(0.3, improvement))


# 创建全局实例
opposition_reviewer = OppositionReviewerAgent(None, None)
