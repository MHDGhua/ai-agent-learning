"""
重庆劳动法专家 Agent
"""

from .base import BaseAgent, AgentCapability
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.blackboard import CaseBlackboard

from app.services.legal_workflow import LegalWorkflowAnalyzer
from app.services.chongqing_precedent import ChongqingPrecedentAdvisor

class ChongqingLaborLawAgent(BaseAgent):
    """重庆劳动法专家 Agent"""
    
    def __init__(self, llm_client, knowledge_base):
        capability = AgentCapability(
            domain="labor_law",
            expertise_level=10,
            supported_tasks=[
                "chongqing_labor_disputes",
                "wage_calculation",
                "work_injury",
                "termination_rules"
            ],
            required_knowledge=[
                "chongqing_labor_regulations",
                "local_policies",
                "chongqing_court_precedents"
            ]
        )
        super().__init__(
            agent_id="cq_labor_001",
            agent_name="重庆劳动法专家",
            capability=capability,
            llm_client=llm_client,
            knowledge_base=knowledge_base
        )
        self.workflow_analyzer = LegalWorkflowAnalyzer()
        self.precedent_advisor = ChongqingPrecedentAdvisor()
    
    async def analyze(self, case_data: Dict[str, Any], blackboard: Optional['CaseBlackboard'] = None) -> Dict[str, Any]:
        """分析重庆劳动法案件，优先输出确定性结构化结果。"""
        description = case_data.get("description", case_data.get("facts", ""))
        workflow = self.workflow_analyzer.analyze(case_data)
        local_reference = self.precedent_advisor.build_local_reference(case_data)
        relevant_laws = []
        if self.knowledge_base:
            try:
                relevant_laws = self.knowledge_base.retrieve(
                    query=f"重庆劳动法 {description}",
                    top_k=5
                ) or []
            except Exception:
                relevant_laws = []

        summary_parts = [
            f"案件类型：{case_data.get('case_type', '劳动纠纷')}",
            f"管辖判断：{'重庆本地管辖要素较明确' if workflow.jurisdiction.get('likely_chongqing_jurisdiction') else '需补充重庆管辖信息'}",
            f"时效判断：{workflow.limitation.get('status', 'unknown')}",
        ]
        if workflow.warnings:
            summary_parts.append(f"风险提示：{'；'.join(workflow.warnings[:2])}")

        return {
            "case_type": case_data.get("case_type", "劳动纠纷"),
            "region_specific_analysis": "重庆",
            "summary": "；".join(summary_parts),
            "jurisdiction": workflow.jurisdiction,
            "limitation": workflow.limitation,
            "claim_items": workflow.claim_items,
            "evidence_checklist": workflow.evidence_checklist,
            "action_plan": workflow.action_plan,
            "negotiation_points": workflow.negotiation_points,
            "legal_basis": workflow.legal_basis,
            "warnings": workflow.warnings,
            "local_reference": local_reference,
            "relevant_laws": relevant_laws[:5],
            "wage_calculation": self._build_wage_hint(case_data),
            "work_injury_assessment": self._build_work_injury_hint(case_data),
            "termination_legality": self._build_termination_hint(case_data, workflow),
            "arbitration_advice": self._build_advice(workflow),
            "confidence": round(self._estimate_confidence(workflow), 2),
            "source": "rule_based",
        }

    def _build_wage_hint(self, case_data: Dict[str, Any]) -> str:
        salary = float(case_data.get("salary") or case_data.get("applicant_info", {}).get("salary") or 0)
        if salary <= 0:
            return "请先补充月工资后再计算拖欠工资或补偿基数。"
        return f"可按月工资约 {salary:.2f} 元作为工资、补偿和加班费计算基数。"

    def _build_work_injury_hint(self, case_data: Dict[str, Any]) -> str:
        facts = f"{case_data.get('case_type', '')}{case_data.get('facts', '')}"
        if "工伤" in facts or "受伤" in facts:
            return "案件包含工伤信号，需先核查工伤认定、劳动能力鉴定和就医记录。"
        return "未见明显工伤信号，可按普通劳动争议路径处理。"

    def _build_termination_hint(self, case_data: Dict[str, Any], workflow) -> str:
        facts = f"{case_data.get('case_type', '')}{case_data.get('facts', '')}"
        if any(keyword in facts for keyword in ["解除", "辞退", "终止"]):
            if workflow.limitation.get("status") == "possibly_expired":
                return "解除类争议存在时效风险，需先核查解除时间和是否存在中断、中止。"
            return "解除类争议应重点核查解除理由、程序和通知时间。"
        return "当前未见明显解除争议信号。"

    def _build_advice(self, workflow) -> str:
        if workflow.warnings:
            return "；".join(workflow.warnings[:3])
        return "可直接进入材料整理、金额拆分和仲裁申请准备。"

    def _estimate_confidence(self, workflow) -> float:
        base = workflow.jurisdiction.get("confidence", 0.5) * 0.6 + 0.3
        if workflow.warnings:
            base -= 0.1
        return max(0.45, min(0.95, base))
    
    async def calculate_compensation(
        self,
        salary: float,
        years_of_service: int,
        termination_type: str
    ) -> float:
        """计算重庆劳动法下的经济补偿金。"""
        multiplier = 2 if "违法" in termination_type else 1
        years = max(0, int(years_of_service))
        salary = max(0.0, float(salary))
        return round(salary * years * multiplier, 2)
    
    async def handle_query(self, sender_id: str, content: Dict[str, Any]):
        """处理重庆劳动法咨询"""
        # 实现具体查询处理逻辑
        pass
    
    async def collaborate(
        self, 
        other_agents: List[BaseAgent], 
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """与其他 Agent 协作"""
        # 重庆劳动法专家可能需要与合同专家协作
        contract_expert = next(
            (a for a in other_agents if "contract_review" in a.capability.supported_tasks),
            None
        )
        
        if contract_expert:
            # 请求合同审查
            contract_review = await contract_expert.analyze(case_data)
            merged_case_data = dict(case_data)
            merged_case_data["contract_review"] = contract_review
            return await self.analyze(merged_case_data)
            
        return await self.analyze(case_data)
