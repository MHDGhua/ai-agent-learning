"""
重庆本地典型案例优先建议层。
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.knowledge.chongqing_guidance import select_relevant_guidance


class ChongqingPrecedentAdvisor:
    """基于重庆公开典型案例和指导意见，给出本地优先分析。"""

    def build_local_reference(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        case_type = str(case_data.get("case_type") or "")
        facts = str(case_data.get("facts") or "")
        applicant_info = case_data.get("applicant_info") or {}
        query = " ".join([
            case_type,
            facts,
            str(applicant_info.get("employer_name") or ""),
            str(applicant_info.get("workplace") or ""),
        ])
        guidance = select_relevant_guidance(query, case_type)
        return {
            "priority": "chongqing_local_first",
            "guidance": guidance,
            "reference_strategy": self._reference_strategy(guidance, query),
        }

    def _reference_strategy(self, guidance: List[Dict[str, Any]], query: str) -> List[str]:
        if not guidance:
            return [
                "先按重庆本地调解/仲裁受理口径确认是否属于劳动争议。",
                "再对照工资、解除、加班、劳动关系认定等本地高频类型补证。",
            ]
        strategy = []
        for item in guidance:
            strategy.append(f"优先参考重庆本地规则：{item['title']}。")
        if any(k in query for k in ["平台", "主播", "骑手", "网约车", "配送"]):
            strategy.append("此类新就业形态案件先按事实优先判断劳动关系，再看管理控制和报酬结算方式。")
        if any(k in query for k in ["解除", "辞退", "终止"]):
            strategy.append("解除类案件重点核查解除理由、程序和作出时间，避免多年后补提解除理由。")
        if any(k in query for k in ["工资", "加班", "报酬"]):
            strategy.append("工资和加班类案件先对齐工资流水、考勤、排班和聊天记录，再算金额。")
        return strategy[:5]
