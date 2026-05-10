"""
Blackboard 共享状态模型

所有 Agent 在分析过程中读写同一个 CaseBlackboard 实例，
实现跨 Agent 的上下文共享，替代原有的 AgentCommunicationBus。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AnalysisStage(str, Enum):
    INTAKE = "intake"
    CLASSIFICATION = "classification"
    WORKFLOW_ANALYSIS = "workflow_analysis"
    LEGAL_OPINION = "legal_opinion"
    PRECEDENT_SEARCH = "precedent_search"
    OPPOSITION_REVIEW = "opposition_review"
    CALCULATION = "calculation"
    DOCUMENT_GENERATION = "document_generation"
    FINAL_SYNTHESIS = "final_synthesis"


@dataclass
class AgentTraceEntry:
    agent_id: str
    agent_name: str
    stage: AnalysisStage
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: float = 0.0
    status: str = "ok"
    summary: str = ""


@dataclass
class CaseBlackboard:
    """所有 Agent 共享的案件分析上下文"""

    case_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    raw_input: Dict[str, Any] = field(default_factory=dict)

    # 分类阶段
    classification: Optional[Dict[str, Any]] = None

    # 工作流分析
    workflow_analysis: Optional[Dict[str, Any]] = None

    # 法律意见
    legal_opinion: Optional[Dict[str, Any]] = None

    # 本地判例参考
    precedent_references: List[Dict[str, Any]] = field(default_factory=list)

    # 红蓝对抗
    red_team_critique: Optional[Dict[str, Any]] = None
    blue_team_critique: Optional[Dict[str, Any]] = None
    opposition_synthesis: Optional[Dict[str, Any]] = None

    # 冲突与协调
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    coordination_notes: List[str] = field(default_factory=list)

    # 赔偿计算
    calculation_results: Optional[Dict[str, Any]] = None

    # 最终综合
    final_synthesis: Optional[Dict[str, Any]] = None

    # 置信度
    confidence_scores: Dict[str, float] = field(default_factory=dict)

    # 审计追踪
    agent_trace: List[AgentTraceEntry] = field(default_factory=list)

    # 当前阶段
    current_stage: AnalysisStage = AnalysisStage.INTAKE

    def record_agent(
        self,
        agent_id: str,
        agent_name: str,
        stage: AnalysisStage,
        *,
        duration_ms: float = 0.0,
        status: str = "ok",
        summary: str = "",
    ) -> None:
        self.agent_trace.append(
            AgentTraceEntry(
                agent_id=agent_id,
                agent_name=agent_name,
                stage=stage,
                duration_ms=duration_ms,
                status=status,
                summary=summary,
            )
        )
        self.current_stage = stage

    def set_confidence(self, agent_id: str, score: float) -> None:
        self.confidence_scores[agent_id] = round(min(1.0, max(0.0, score)), 3)

    def get_context_for_agent(self, stage: AnalysisStage) -> Dict[str, Any]:
        """根据当前阶段，返回该 Agent 可读取的上游结果摘要"""
        ctx: Dict[str, Any] = {"case_id": self.case_id, "raw_input": self.raw_input}
        if stage.value != AnalysisStage.CLASSIFICATION.value and self.classification:
            ctx["classification"] = self.classification
        if stage.value not in (AnalysisStage.CLASSIFICATION.value, AnalysisStage.WORKFLOW_ANALYSIS.value):
            if self.workflow_analysis:
                ctx["workflow_analysis"] = self.workflow_analysis
        if self.legal_opinion and stage in (
            AnalysisStage.OPPOSITION_REVIEW,
            AnalysisStage.FINAL_SYNTHESIS,
        ):
            ctx["legal_opinion"] = self.legal_opinion
        if self.precedent_references:
            ctx["precedent_references"] = self.precedent_references
        if stage == AnalysisStage.FINAL_SYNTHESIS:
            ctx["red_team_critique"] = self.red_team_critique
            ctx["blue_team_critique"] = self.blue_team_critique
            ctx["conflicts"] = self.conflicts
        return ctx

    def to_summary(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "current_stage": self.current_stage.value,
            "agents_involved": len(self.agent_trace),
            "conflicts_count": len(self.conflicts),
            "confidence_scores": self.confidence_scores,
            "has_opposition_review": self.opposition_synthesis is not None,
        }
