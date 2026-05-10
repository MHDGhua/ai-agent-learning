"""
劳动仲裁流程化分析。

本模块只做确定性规则分析：管辖、时效、诉求、证据和行动清单。
可变的地方标准保留在 calculator/config 层，避免把易过期数值写死在流程判断中。
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Any, Dict, List, Optional


STABLE_LEGAL_BASIS = {
    "scope": "《中华人民共和国劳动争议调解仲裁法》第二条",
    "process": "《中华人民共和国劳动争议调解仲裁法》第五条",
    "limitation": "《中华人民共和国劳动争议调解仲裁法》第二十七条",
    "free_arbitration": "《中华人民共和国劳动争议调解仲裁法》第五十三条",
    "severance": "《中华人民共和国劳动合同法》第四十七条",
    "illegal_termination": "《中华人民共和国劳动合同法》第四十八条、第八十七条",
    "burden": "《最高人民法院关于审理劳动争议案件适用法律问题的解释（一）》第四十四条",
}


@dataclass
class WorkflowAnalysis:
    jurisdiction: Dict[str, Any]
    limitation: Dict[str, Any]
    claim_items: List[Dict[str, Any]]
    evidence_checklist: List[Dict[str, Any]]
    action_plan: List[str]
    negotiation_points: List[str]
    legal_basis: List[str]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LegalWorkflowAnalyzer:
    """把用户事实拆成可执行的仲裁准备清单。"""

    LABOR_KEYWORDS = ["工资", "加班", "辞退", "解除", "离职", "工伤", "社保", "补偿", "赔偿", "劳动合同", "年休假", "竞业"]
    CHONGQING_KEYWORDS = ["重庆", "渝中", "江北", "渝北", "沙坪坝", "九龙坡", "南岸", "巴南", "北碚", "万州", "涪陵"]

    def analyze(self, case_data: Dict[str, Any], today: Optional[date] = None) -> WorkflowAnalysis:
        today = today or date.today()
        case_type = str(case_data.get("case_type") or "劳动纠纷")
        facts = str(case_data.get("facts") or "")
        applicant_info = case_data.get("applicant_info") or {}
        evidence = [str(e) for e in case_data.get("evidence") or []]

        jurisdiction = self._analyze_jurisdiction(case_type, facts, applicant_info)
        limitation = self._analyze_limitation(case_type, facts, applicant_info, today)
        claim_items = self._build_claim_items(case_type, facts, applicant_info)
        evidence_checklist = self._build_evidence_checklist(case_type, facts, evidence)
        warnings = self._build_warnings(jurisdiction, limitation, case_data)
        action_plan = self._build_action_plan(jurisdiction, limitation, warnings)
        negotiation_points = self._build_negotiation_points(claim_items)
        legal_basis = self._select_legal_basis(case_type, claim_items)

        return WorkflowAnalysis(
            jurisdiction=jurisdiction,
            limitation=limitation,
            claim_items=claim_items,
            evidence_checklist=evidence_checklist,
            action_plan=action_plan,
            negotiation_points=negotiation_points,
            legal_basis=legal_basis,
            warnings=warnings,
        )

    def _add_years_safe(self, source: date, years: int) -> date:
        """避免 2 月 29 日等日期在加一年时抛异常。"""
        try:
            return source.replace(year=source.year + years)
        except ValueError:
            # 2 月 29 日顺延到 2 月 28 日，保证时效判断稳定可测
            return source.replace(month=2, day=28, year=source.year + years)

    def _analyze_jurisdiction(self, case_type: str, facts: str, applicant_info: Dict[str, Any]) -> Dict[str, Any]:
        text = " ".join([
            case_type,
            facts,
            str(applicant_info.get("employer_name") or ""),
            str(applicant_info.get("workplace") or ""),
            str(applicant_info.get("contract_place") or ""),
            str(applicant_info.get("employer_address") or ""),
        ])
        is_labor = any(keyword in text for keyword in self.LABOR_KEYWORDS)
        cq_signals = [keyword for keyword in self.CHONGQING_KEYWORDS if keyword in text]
        confidence = 0.35
        if is_labor:
            confidence += 0.3
        if cq_signals:
            confidence += 0.25
        if applicant_info.get("employer_name"):
            confidence += 0.05

        return {
            "is_labor_dispute": is_labor,
            "likely_chongqing_jurisdiction": bool(cq_signals),
            "confidence": round(min(confidence, 0.95), 2),
            "signals": cq_signals,
            "suggested_forum": "重庆市劳动人事争议仲裁委员会或用人单位所在地/劳动合同履行地对应区县仲裁委" if cq_signals else "需补充工作地、合同履行地或用人单位所在地后判断",
            "missing": self._missing_jurisdiction_fields(applicant_info, cq_signals),
        }

    def _missing_jurisdiction_fields(self, applicant_info: Dict[str, Any], cq_signals: List[str]) -> List[str]:
        missing = []
        if not applicant_info.get("employer_name"):
            missing.append("用人单位全称")
        if not applicant_info.get("workplace") and not applicant_info.get("contract_place") and not cq_signals:
            missing.append("实际工作地或劳动合同履行地")
        if not applicant_info.get("employer_address"):
            missing.append("用人单位注册地址或办公地址")
        return missing

    def _analyze_limitation(
        self,
        case_type: str,
        facts: str,
        applicant_info: Dict[str, Any],
        today: date,
    ) -> Dict[str, Any]:
        dispute_date = self._parse_date(applicant_info.get("dispute_date") or applicant_info.get("termination_date"))
        termination_date = self._parse_date(applicant_info.get("termination_date"))
        is_wage_claim = any(keyword in case_type + facts for keyword in ["工资", "劳动报酬", "加班费"])
        still_employed = bool(applicant_info.get("still_employed", False))
        anchor_date = dispute_date
        if not anchor_date and is_wage_claim and termination_date:
            anchor_date = termination_date

        if not anchor_date:
            return {
                "status": "unknown",
                "days_elapsed": None,
                "deadline": None,
                "rule": "一般劳动争议仲裁时效为一年；拖欠劳动报酬在劳动关系存续期间不受一年限制，终止后应在一年内提出。",
                "missing": ["争议发生日期", "离职或劳动关系终止日期"],
            }

        days_elapsed = (today - anchor_date).days
        deadline = self._add_years_safe(anchor_date, 1)
        status = "within_period" if days_elapsed <= 365 else "possibly_expired"
        special_note = None

        if is_wage_claim and still_employed:
            status = "wage_claim_during_employment"
            special_note = "拖欠劳动报酬且劳动关系仍存续时，通常不按一般一年时效限制处理。"
        elif is_wage_claim and termination_date:
            deadline = self._add_years_safe(termination_date, 1)
            days_elapsed = (today - termination_date).days
            status = "within_period" if days_elapsed <= 365 else "possibly_expired"
            special_note = "劳动关系终止后的拖欠劳动报酬，应以终止之日起一年内提出为重点核查。"

        return {
            "status": status,
            "days_elapsed": max(days_elapsed, 0),
            "deadline": deadline.isoformat(),
            "rule": "一般劳动争议仲裁时效为一年；拖欠劳动报酬有特别规则。",
            "special_note": special_note,
            "missing": [],
        }

    def _build_claim_items(self, case_type: str, facts: str, applicant_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = case_type + facts
        claims: List[Dict[str, Any]] = []
        has_annual_leave_claim = any(k in text for k in ["未休年假", "年休假", "年假"])

        if has_annual_leave_claim:
            claims.append({
                "name": "未休年休假工资",
                "priority": "medium",
                "calculation": "核查应休未休天数、日工资基数和是否已安排休假或支付补偿",
                "basis": "《职工带薪年休假条例》",
            })
        if any(k in text for k in ["拖欠", "欠薪", "劳动报酬"]) or ("工资" in text and not has_annual_leave_claim):
            claims.append({
                "name": "拖欠工资/劳动报酬",
                "priority": "high",
                "calculation": "按欠付月份、月工资、已支付金额逐项列明",
                "basis": STABLE_LEGAL_BASIS["scope"],
            })
        if "加班" in text:
            claims.append({
                "name": "加班费",
                "priority": "high",
                "calculation": "区分工作日、休息日、法定节假日，结合考勤和工资基数计算",
                "basis": "《中华人民共和国劳动法》第四十四条",
            })
        if any(k in text for k in ["辞退", "违法解除", "解除"]):
            claims.append({
                "name": "违法解除赔偿金或经济补偿金",
                "priority": "high",
                "calculation": "先判断解除是否合法；违法解除通常按经济补偿标准二倍主张",
                "basis": STABLE_LEGAL_BASIS["illegal_termination"],
            })
        if "未签" in text or "没签" in text:
            claims.append({
                "name": "未签书面劳动合同二倍工资差额",
                "priority": "medium",
                "calculation": "核查入职满一个月后至满一年期间的工资差额",
                "basis": "《中华人民共和国劳动合同法》第八十二条",
            })
        if "工伤" in text or "受伤" in text:
            claims.append({
                "name": "工伤待遇",
                "priority": "high",
                "calculation": "先确认工伤认定、劳动能力鉴定，再分项核算医疗费、停工留薪期工资、伤残待遇等",
                "basis": "《工伤保险条例》",
            })
        if "社保" in text:
            claims.append({
                "name": "社会保险相关处理",
                "priority": "medium",
                "calculation": "社保补缴通常优先向社保经办或行政部门投诉处理，涉及赔偿再结合仲裁请求设计",
                "basis": "《中华人民共和国社会保险法》",
            })

        if not claims:
            claims.append({
                "name": "确认劳动关系/基础劳动争议请求",
                "priority": "medium",
                "calculation": "先明确劳动关系、争议发生时间、具体金额和事实依据",
                "basis": STABLE_LEGAL_BASIS["scope"],
            })
        return claims

    def _build_evidence_checklist(self, case_type: str, facts: str, existing_evidence: List[str]) -> List[Dict[str, Any]]:
        text = case_type + facts
        checklist = [
            ("劳动关系", ["劳动合同", "入职登记表", "工作证", "工牌", "社保记录", "工资流水"]),
            ("用人单位信息", ["营业执照信息", "公司注册地址", "办公地址", "法定代表人信息"]),
            ("工资标准", ["工资条", "银行流水", "薪酬确认记录", "个税记录"]),
        ]
        if "加班" in text:
            checklist.append(("加班事实", ["考勤记录", "排班表", "加班审批", "工作群通知", "邮件记录"]))
        if any(k in text for k in ["辞退", "解除"]):
            checklist.append(("解除事实", ["解除通知", "谈话录音", "离职交接记录", "公司规章制度", "处罚记录"]))
        if "工伤" in text or "受伤" in text:
            checklist.append(("工伤事实", ["事故经过说明", "就医记录", "诊断证明", "报警或现场记录", "证人证言"]))
        if any(k in text for k in ["未休年假", "年休假", "年假"]):
            checklist.append(("年休假情况", ["入职时间证明", "休假记录", "考勤记录", "工资流水", "离职结算单"]))

        existing_text = " ".join(existing_evidence)
        return [
            {
                "category": category,
                "items": items,
                "status": "partially_ready" if any(item in existing_text for item in items) else "missing",
            }
            for category, items in checklist
        ]

    def _build_action_plan(
        self,
        jurisdiction: Dict[str, Any],
        limitation: Dict[str, Any],
        warnings: List[str],
    ) -> List[str]:
        plan = [
            "整理时间线：入职、岗位/工资变化、争议发生、沟通催告、离职或解除时间。",
            "按诉求拆金额：每项请求单独列计算口径、期间、金额和证据。",
            "补齐证据目录：每份证据写明证明目的，保留原件和电子记录原始载体。",
        ]
        if jurisdiction.get("missing"):
            plan.insert(0, "先补充用人单位所在地、实际工作地或合同履行地，用于确定重庆具体区县仲裁委。")
        if limitation.get("status") == "possibly_expired":
            plan.insert(0, "优先核查仲裁时效是否中断、中止，尽快提交申请或咨询律师。")
        if not warnings:
            plan.append("向对应劳动人事争议仲裁委员会提交申请书、身份证明、主体信息和证据副本。")
        return plan

    def _build_negotiation_points(self, claim_items: List[Dict[str, Any]]) -> List[str]:
        points = ["以书面方式固定沟通记录，避免只做口头协商。"]
        for claim in claim_items[:3]:
            points.append(f"围绕“{claim['name']}”明确底线金额、可让步范围和付款期限。")
        return points

    def _select_legal_basis(self, case_type: str, claim_items: List[Dict[str, Any]]) -> List[str]:
        basis = [
            STABLE_LEGAL_BASIS["scope"],
            STABLE_LEGAL_BASIS["process"],
            STABLE_LEGAL_BASIS["limitation"],
            STABLE_LEGAL_BASIS["free_arbitration"],
        ]
        for claim in claim_items:
            claim_basis = claim.get("basis")
            if claim_basis and claim_basis not in basis:
                basis.append(claim_basis)
        if any("解除" in claim["name"] for claim in claim_items):
            basis.append(STABLE_LEGAL_BASIS["burden"])
        return basis

    def _build_warnings(
        self,
        jurisdiction: Dict[str, Any],
        limitation: Dict[str, Any],
        case_data: Dict[str, Any],
    ) -> List[str]:
        warnings = []
        if not jurisdiction.get("is_labor_dispute"):
            warnings.append("目前事实不足以确认属于劳动争议，需先核实是否存在劳动关系。")
        if not jurisdiction.get("likely_chongqing_jurisdiction"):
            warnings.append("重庆管辖依据不足，需补充工作地、合同履行地或用人单位所在地。")
        if limitation.get("status") == "possibly_expired":
            warnings.append("可能超过一年仲裁时效，需要核查中断、中止或特殊时效规则。")
        if not case_data.get("evidence"):
            warnings.append("证据为空，当前建议只能作为信息补全指引。")
        return warnings

    def _parse_date(self, raw: Any) -> Optional[date]:
        if isinstance(raw, date):
            return raw
        if not raw:
            return None
        text = str(raw).strip()
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None
