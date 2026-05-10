#!/usr/bin/env python3
"""
劳动仲裁文书生成器
使用 Jinja2 模板引擎渲染文书，数据准备逻辑保留在 Python 中。
"""

from pathlib import Path
from typing import Dict, List, Any
from enum import Enum

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


class DocumentType(str, Enum):
    ARBITRATION_APPLICATION = "仲裁申请书"
    MEDIATION_APPLICATION = "庭前调解申请书"
    DEFENSE_RESPONSE = "答辩书"
    EVIDENCE_LIST = "证据清单"
    PROXY_LETTER = "代理词"


_TEMPLATE_MAP = {
    DocumentType.ARBITRATION_APPLICATION: "arbitration_application.j2",
    DocumentType.MEDIATION_APPLICATION: "mediation_application.j2",
    DocumentType.DEFENSE_RESPONSE: "defense_response.j2",
    DocumentType.EVIDENCE_LIST: "evidence_list.j2",
    DocumentType.PROXY_LETTER: "proxy_letter.j2",
}


class ArbitrationDocumentGenerator:

    def __init__(self):
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def _applicant_info(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        return case_data.get("applicant_info") or {}

    def _money(self, value: Any) -> str:
        try:
            amount = float(value or 0)
        except (TypeError, ValueError):
            amount = 0
        return f"{amount:,.2f}".replace(",", "") if amount else "______"

    def _build_claim_requests(self, case_data: Dict[str, Any]) -> List[str]:
        text = f"{case_data.get('case_type', '')} {case_data.get('facts', '')}"
        salary = case_data.get("salary") or self._applicant_info(case_data).get("salary")
        amount = case_data.get("amount")
        requests: List[str] = []

        if any(k in text for k in ["工资", "拖欠", "劳动报酬"]):
            requests.append(f"请求裁决被申请人支付拖欠工资人民币{self._money(amount)}元。")
        if "加班" in text:
            requests.append("请求裁决被申请人支付延时、休息日或法定节假日加班工资，具体金额以工资基数、考勤和庭审核算为准。")
        if any(k in text for k in ["辞退", "违法解除", "解除"]):
            requests.append("请求裁决被申请人支付违法解除劳动合同赔偿金或经济补偿金。")
        if "未签" in text or "没签" in text:
            requests.append("请求裁决被申请人支付未签书面劳动合同二倍工资差额。")
        if "工伤" in text or "受伤" in text:
            requests.append("请求裁决被申请人依法承担工伤待遇相关费用。")

        if not requests:
            requests.append("请求依法确认双方劳动关系并支持申请人的劳动争议请求。")
        if salary:
            requests.append(f"请求以月工资人民币{self._money(salary)}元作为相关项目的计算基数。")
        return requests

    def _build_evidence_rows(self, case_data: Dict[str, Any]) -> List[Dict[str, str]]:
        evidence = [str(item).strip() for item in case_data.get("evidence") or [] if str(item).strip()]
        rows = []
        defaults = {
            "劳动合同": "证明双方存在劳动关系、岗位、工资及合同期限。",
            "工资流水": "证明工资标准、支付周期及欠付事实。",
            "聊天记录": "证明工作安排、催款沟通或解除过程。",
            "考勤记录": "证明出勤、加班时长及排班情况。",
            "解除通知": "证明用人单位解除劳动关系的时间和理由。",
        }
        for item in evidence:
            purpose = next((text for key, text in defaults.items() if key in item), "证明与本案争议相关的事实。")
            rows.append({"name": item, "purpose": purpose})
        if not rows:
            rows = [{"name": "待补充证据", "purpose": "请补充劳动合同、工资流水、聊天记录、考勤或解除通知等材料。"}]
        return rows

    def _prepare_context(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        applicant_info = self._applicant_info(case_data)
        evidence_rows = self._build_evidence_rows(case_data)
        return {
            "case_type": case_data.get("case_type", "劳动纠纷"),
            "facts": case_data.get("facts") or "请在此处详细描述案件事实经过，包括入职时间、工作岗位、工资标准、争议发生的时间、地点、原因及经过等。",
            "applicant_name": applicant_info.get("name", "申请人"),
            "respondent_name": applicant_info.get("employer_name", "被申请人"),
            "respondent_address": applicant_info.get("employer_address") or applicant_info.get("workplace") or "____________________________________________",
            "phone": case_data.get("contact_phone") or applicant_info.get("phone") or "________________________________________",
            "claim_requests": self._build_claim_requests(case_data),
            "evidence_rows": evidence_rows,
            "evidence_names": "、".join(row["name"] for row in evidence_rows),
        }

    async def generate_arbitration_document(
        self,
        document_type: DocumentType,
        case_data: Dict[str, Any]
    ) -> str:
        template_name = _TEMPLATE_MAP.get(document_type)
        if not template_name:
            raise ValueError(f"不支持的文书类型：{document_type}")

        template = self._env.get_template(template_name)
        context = self._prepare_context(case_data)
        return template.render(**context)
