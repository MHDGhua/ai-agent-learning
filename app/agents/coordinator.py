"""协调仲裁者 Agent。"""

import time
from typing import Dict, Any, List, Optional
from .base import BaseAgent, AgentCapability
from .chongqing_labor_law import ChongqingLaborLawAgent
import json

from app.core.blackboard import CaseBlackboard, AnalysisStage
from app.services.legal_workflow import LegalWorkflowAnalyzer


class CoordinatorAgent(BaseAgent):
    """协调仲裁者 Agent"""

    def __init__(self, llm_client, knowledge_base):
        capability = AgentCapability(
            domain="coordination",
            expertise_level=10,
            supported_tasks=["coordination", "conflict_resolution", "decision_making"],
            required_knowledge=["decision_rules", "voting_protocols"]
        )
        super().__init__(
            agent_id="coordinator_001",
            agent_name="协调仲裁者",
            capability=capability,
            llm_client=llm_client,
            knowledge_base=knowledge_base
        )
        self.registered_agents = {}
        self.active_cases = {}
        self.workflow_analyzer = LegalWorkflowAnalyzer()

    async def analyze(self, case_data: Dict[str, Any], blackboard: Optional[CaseBlackboard] = None) -> Dict[str, Any]:
        workflow = self.workflow_analyzer.analyze(case_data)
        result = {
            "summary": "已接收案件，可协调重庆劳动法专家和对抗审查流程。",
            "case_type": case_data.get("case_type", "劳动纠纷"),
            "workflow": workflow.to_dict(),
            "recommendations": workflow.action_plan[:3],
        }
        if blackboard:
            blackboard.workflow_analysis = workflow.to_dict()
            blackboard.record_agent(
                self.agent_id, self.agent_name, AnalysisStage.WORKFLOW_ANALYSIS,
                summary="基础协调意见已生成",
            )
        return result

    async def collaborate(
        self,
        other_agents: List[BaseAgent],
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self.analyze(case_data)

    async def register_agent(self, agent: BaseAgent):
        self.registered_agents[agent.agent_id] = agent

    async def coordinate_labor_analysis(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        labor_agent: ChongqingLaborLawAgent,
        blackboard: Optional[CaseBlackboard] = None,
    ) -> Dict[str, Any]:
        """协调多个 Agent 进行分析，结果写入 blackboard"""

        if blackboard is None:
            blackboard = CaseBlackboard(case_id=case_id, raw_input=case_data)

        workflow = self.workflow_analyzer.analyze(case_data).to_dict()
        blackboard.workflow_analysis = workflow
        blackboard.record_agent(
            self.agent_id, self.agent_name, AnalysisStage.WORKFLOW_ANALYSIS,
            summary="工作流分析完成",
        )

        self.active_cases[case_id] = {
            "status": "processing",
            "agents": {labor_agent.agent_id: None},
            "workflow": workflow,
        }

        t0 = time.perf_counter()
        labor_result = await labor_agent.analyze(case_data, blackboard=blackboard)
        labor_result = self._normalize_agent_result(labor_result)
        duration = (time.perf_counter() - t0) * 1000

        blackboard.legal_opinion = labor_result
        blackboard.set_confidence(labor_agent.agent_id, labor_result.get("confidence", 0.85))
        blackboard.record_agent(
            labor_agent.agent_id, labor_agent.agent_name, AnalysisStage.LEGAL_OPINION,
            duration_ms=duration, summary=labor_result.get("summary", "")[:100],
        )

        agent_results = {
            labor_agent.agent_id: {
                "agent_name": labor_agent.agent_name,
                "analysis": labor_result,
                "confidence": labor_result.get("confidence", 0.85),
                "role": "primary",
            }
        }

        conflicts = self._detect_conflicts(agent_results, workflow)
        if conflicts:
            blackboard.conflicts = conflicts
            resolved = await self._resolve_conflicts(conflicts, agent_results, workflow)
            agent_results.update(resolved)

        final_opinion = await self._generate_final_opinion(case_data, agent_results, workflow)
        recommendations = self._generate_recommendations(final_opinion, workflow)

        blackboard.final_synthesis = final_opinion
        blackboard.coordination_notes = recommendations
        blackboard.record_agent(
            self.agent_id, self.agent_name, AnalysisStage.FINAL_SYNTHESIS,
            summary="最终意见已生成",
        )

        self.active_cases[case_id].update({
            "status": "completed",
            "final_opinion": final_opinion,
            "conflicts_detected": len(conflicts) > 0,
            "recommendations": recommendations,
        })

        return {
            "case_id": case_id,
            "agent_analyses": agent_results,
            "conflicts_detected": len(conflicts) > 0,
            "final_opinion": final_opinion,
            "recommendations": recommendations,
            "workflow": workflow,
            "blackboard_summary": blackboard.to_summary(),
        }

    def _normalize_agent_result(self, result: Any) -> Dict[str, Any]:
        if isinstance(result, dict):
            return result
        return {"summary": str(result), "confidence": 0.5}

    def _detect_conflicts(
        self,
        agent_results: Dict[str, Any],
        workflow: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        conflicts: List[Dict[str, Any]] = []
        workflow_warnings = workflow.get("warnings", []) or []
        limitation = workflow.get("limitation", {}) or {}
        jurisdiction = workflow.get("jurisdiction", {}) or {}

        for agent_id, info in agent_results.items():
            analysis = info.get("analysis", {}) or {}
            summary = str(analysis.get("summary") or "")
            confidence = float(info.get("confidence", analysis.get("confidence", 0.0)) or 0.0)
            if limitation.get("status") == "possibly_expired" and "时效" not in summary:
                conflicts.append({
                    "agent1": agent_id,
                    "agent2": "workflow",
                    "issue": "仲裁时效风险未被充分提示",
                })
            if jurisdiction.get("missing") and "补充" not in summary and confidence >= 0.8:
                conflicts.append({
                    "agent1": agent_id,
                    "agent2": "workflow",
                    "issue": "管辖要素缺失但结论表述过于肯定",
                })
            if workflow_warnings and confidence >= 0.85 and not analysis.get("risk_factors"):
                conflicts.append({
                    "agent1": agent_id,
                    "agent2": "workflow",
                    "issue": "风险提示与结构化分析未对齐",
                })
        return conflicts

    async def _resolve_conflicts(
        self,
        conflicts: List[Dict[str, Any]],
        agent_results: Dict[str, Any],
        workflow: Dict[str, Any],
    ) -> Dict[str, Any]:
        conflict_descriptions = [f"{c['agent1']}->{c['issue']}" for c in conflicts]
        resolution_note = "；".join(conflict_descriptions)
        if self.llm_client:
            try:
                prompt = (
                    "请根据以下冲突给出简洁的协调意见，只输出结论文本：\n"
                    f"{json.dumps(conflicts, ensure_ascii=False)}\n"
                    f"案件流程信息：{json.dumps(workflow, ensure_ascii=False)}"
                )
                resolution = await self.llm_client.generate_text(prompt)
                if resolution and resolution.strip() and resolution.strip() != "本地模式下已生成基础分析结果。":
                    resolution_note = resolution.strip()
            except Exception:
                pass

        resolved = {}
        for agent_id, info in agent_results.items():
            analysis = dict(info.get("analysis", {}) or {})
            analysis.setdefault("coordination_notes", [])
            analysis["coordination_notes"].append(resolution_note)
            analysis["risk_factors"] = list(dict.fromkeys((analysis.get("risk_factors") or []) + [c["issue"] for c in conflicts]))
            resolved[agent_id] = {
                **info,
                "analysis": analysis,
                "confidence": round(max(0.0, float(info.get("confidence", 0.5)) - 0.05 * len(conflicts)), 3),
                "resolution_note": resolution_note,
            }
        return resolved

    async def _generate_final_opinion(
        self,
        case_data: Dict[str, Any],
        agent_results: Dict[str, Any],
        workflow: Dict[str, Any],
    ) -> Dict[str, Any]:
        analyses = []
        for info in agent_results.values():
            analysis = info.get("analysis", {}) or {}
            analyses.append({
                "agent_name": info.get("agent_name"),
                "summary": analysis.get("summary", json.dumps(analysis, ensure_ascii=False)),
                "confidence": info.get("confidence", analysis.get("confidence", 0.0)),
            })

        prompt = (
            "你作为法律专家协调者，需要综合以下分析结果形成最终意见，只输出正文：\n"
            f"案件描述：{case_data.get('description', case_data.get('facts', ''))}\n"
            f"案件流程：{json.dumps(workflow, ensure_ascii=False)}\n"
            f"各专家分析：{json.dumps(analyses, ensure_ascii=False)}"
        )

        final_opinion_text = ""
        if self.llm_client:
            try:
                final_opinion_text = await self.llm_client.generate_text(prompt)
            except Exception:
                final_opinion_text = ""
        if not final_opinion_text or final_opinion_text.strip() == "本地模式下已生成基础分析结果。":
            final_opinion_text = self._compose_local_final_opinion(case_data, agent_results, workflow)
        return {
            "summary": final_opinion_text,
            "analysis_details": agent_results
        }

    def _compose_local_final_opinion(
        self,
        case_data: Dict[str, Any],
        agent_results: Dict[str, Any],
        workflow: Dict[str, Any],
    ) -> str:
        agent_names = "、".join(info.get("agent_name", "未知Agent") for info in agent_results.values())
        key_points = []
        if workflow.get("jurisdiction", {}).get("missing"):
            key_points.append("管辖信息需要补齐")
        if workflow.get("limitation", {}).get("status") == "possibly_expired":
            key_points.append("仲裁时效需优先核查")
        if not key_points:
            key_points.append("事实和证据可直接推进材料整理")
        return (
            f"本案已由{agent_names}完成协同分析。"
            f"案件类型为{case_data.get('case_type', '劳动纠纷')}，"
            f"核心关注点：{'；'.join(key_points)}。"
            "建议优先按照流程清单补齐事实、证据和金额口径，再进入对抗审查。"
        )

    def _generate_recommendations(self, final_opinion: Dict[str, Any], workflow: Dict[str, Any]) -> List[str]:
        recommendations = list(workflow.get("action_plan", []) or [])
        if workflow.get("limitation", {}).get("status") == "possibly_expired":
            recommendations.insert(0, "优先核查仲裁时效是否存在中断或中止。")
        if workflow.get("jurisdiction", {}).get("missing"):
            recommendations.insert(0, "先补齐管辖要素，再确定递交对应仲裁委。")
        if not recommendations:
            recommendations = ["进一步补齐证据后再推进仲裁材料。"]
        summary = final_opinion.get("summary", "")
        if summary and "对抗审查" not in summary:
            recommendations.append("如需提高论证强度，可再进行一次红蓝对抗审查。")
        return list(dict.fromkeys(recommendations))[:6]

    async def handle_query(self, sender_id: str, content: Dict[str, Any]):
        pass

    async def handle_broadcast(self, sender_id: str, content: Dict[str, Any]):
        pass

    async def conduct_opposition_review(
        self,
        case_data: Dict[str, Any],
        original_analysis: Dict[str, Any],
        blackboard: Optional[CaseBlackboard] = None,
    ) -> Dict[str, Any]:
        from app.agents.red_blue_lawyer import OppositionReviewerAgent
        reviewer = OppositionReviewerAgent(self.llm_client, self.knowledge_base)
        result = await reviewer.conduct_opposition_review(case_data, original_analysis)
        if blackboard:
            blackboard.opposition_synthesis = result
            blackboard.record_agent(
                self.agent_id, self.agent_name, AnalysisStage.OPPOSITION_REVIEW,
                summary="红蓝对抗审查完成",
            )
        return result
