"""Run a visible 20-case backend stability matrix.

This script exercises the public `/arbitration/workup` API through FastAPI's
TestClient and writes a per-case status report for operators.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from fastapi.testclient import TestClient

os.environ.setdefault("LLM_PROVIDER", "local")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.api.main import create_app

OUTPUT_DIR = PROJECT_ROOT / "output"


def case_payload(
    identity: str,
    case_type: str,
    facts: str,
    evidence: List[str],
    *,
    salary: float = 8000,
    years: float = 2,
    workplace: str = "重庆市渝北区",
    employer_name: str = "重庆某公司",
    evidence_quality: str = "一般",
    applicant_background: str = "普通员工",
    expected_keywords: List[str] | None = None,
) -> Dict[str, Any]:
    return {
        "identity": identity,
        "expected_keywords": expected_keywords or [],
        "request": {
            "case_type": case_type,
            "facts": facts,
            "evidence": evidence,
            "salary": salary,
            "years": years,
            "amount": salary * max(1, years),
            "evidence_quality": evidence_quality,
            "applicant_background": applicant_background,
            "enable_opposition_review": True,
            "applicant_info": {
                "name": identity,
                "employer_name": employer_name,
                "workplace": workplace,
                "employer_address": workplace,
                "start_date": "2023-03-01",
                "salary": salary,
            },
        },
    }


def build_cases() -> List[Dict[str, Any]]:
    return [
        case_payload("外卖骑手", "新就业形态劳动关系确认", "平台长期排班管理并按月结算报酬，现否认劳动关系。", ["接单记录", "排班截图", "聊天记录"], expected_keywords=["劳动关系"]),
        case_payload("餐饮服务员", "工资报酬纠纷", "餐馆拖欠三个月工资，老板口头承诺一直未支付。", ["工资流水", "聊天记录"], salary=5200, expected_keywords=["工资"]),
        case_payload("工厂普工", "加班费纠纷", "长期周末加班，考勤和排班表显示未支付加班费。", ["考勤记录", "排班表"], salary=6500, expected_keywords=["加班"]),
        case_payload("销售经理", "违法解除劳动合同纠纷", "公司未说明理由直接解除劳动合同并停发工资。", ["解除通知", "工资流水"], salary=16000, applicant_background="管理层", expected_keywords=["解除"]),
        case_payload("保安", "未签书面劳动合同争议", "入职超过半年未签劳动合同，只通过微信安排工作。", ["工作群记录", "工资流水"], salary=4800, expected_keywords=["合同"]),
        case_payload("建筑工人", "工伤待遇争议", "在重庆工地施工受伤，已就医但单位不配合处理工伤。", ["诊断证明", "事故照片"], salary=9000, expected_keywords=["工伤"]),
        case_payload("幼儿园老师", "社保争议", "学校多年未足额缴纳社保，离职后要求处理。", ["社保记录", "工资流水"], salary=7000, expected_keywords=["社会保险"]),
        case_payload("主播", "新就业形态劳动关系确认", "公司规定直播时长、考核和处罚，但合同写合作协议。", ["合作协议", "排班表", "处罚记录"], salary=12000, expected_keywords=["劳动关系"]),
        case_payload("网约车司机", "劳动关系确认纠纷", "车辆和订单由公司统一管理，收入按月结算。", ["派单记录", "工资流水"], salary=10000, expected_keywords=["劳动关系"]),
        case_payload("超市收银员", "工资报酬纠纷", "离职后最后一个月工资和押金未退。", ["离职交接", "工资流水"], salary=4500, expected_keywords=["工资"]),
        case_payload("仓库管理员", "违法解除劳动合同纠纷", "公司以旷工为由辞退，但实际是调岗争议未协商一致。", ["调岗通知", "聊天记录"], salary=7800, expected_keywords=["解除"]),
        case_payload("客服专员", "竞业限制纠纷", "离职后公司要求履行竞业限制，但未支付补偿。", ["竞业协议", "离职证明"], salary=9000, expected_keywords=["竞业"]),
        case_payload("护士", "加班费纠纷", "夜班和节假日值班较多，单位未依法支付加班费。", ["排班表", "考勤记录"], salary=8500, expected_keywords=["加班"]),
        case_payload("快递分拣员", "工伤待遇争议", "分拣货物时受伤，单位称不是工作原因。", ["诊断证明", "监控截图"], salary=6200, expected_keywords=["工伤"]),
        case_payload("行政文员", "未休年假工资纠纷", "工作三年从未安排年休假，离职时未折算工资。", ["劳动合同", "离职证明"], salary=6800, expected_keywords=["年休假"]),
        case_payload("设计师", "拖欠提成纠纷", "公司拖欠项目提成和绩效奖金，合同及聊天记录可证明。", ["劳动合同", "聊天记录", "项目确认单"], salary=11000, expected_keywords=["工资"]),
        case_payload("实习生", "实习劳务关系争议", "以实习名义长期全职工作并接受公司管理，报酬按月发放。", ["实习协议", "考勤记录"], salary=3500, expected_keywords=["劳动关系"]),
        case_payload("家政人员", "劳务/劳动关系争议", "通过公司派单上门服务，公司统一收费和管理。", ["派单记录", "结算记录"], salary=6000, expected_keywords=["劳动关系"]),
        case_payload("物业维修工", "工资报酬纠纷", "物业公司拖欠工资并要求先签离职协议才付款。", ["工资流水", "离职协议草稿"], salary=6200, expected_keywords=["工资"]),
        case_payload("货车司机", "违法解除及欠薪纠纷", "公司拖欠工资后又口头辞退，未出具书面解除材料。", ["运输记录", "聊天记录", "工资流水"], salary=9500, expected_keywords=["工资", "解除"]),
    ]


def summarize_case(index: int, case: Dict[str, Any], payload: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
    analysis = response.get("analysis", {})
    claim_names = [item.get("name", "") for item in analysis.get("claim_items") or []]
    joined_claims = " ".join(claim_names)
    expected_keywords = case["expected_keywords"]
    keyword_hit = not expected_keywords or any(keyword in joined_claims or keyword in analysis.get("case_type", "") for keyword in expected_keywords)
    required_fields = ["analysis", "intake", "success_prediction", "suggested_documents", "service_recommendation"]
    has_required = all(field in response for field in required_fields)
    status = "PASS" if keyword_hit and has_required else "CHECK"

    return {
        "index": index,
        "identity": case["identity"],
        "input_case_type": payload["case_type"],
        "status": status,
        "workflow_stage": response.get("workflow_stage", ""),
        "risk_level": analysis.get("risk_level", ""),
        "success_probability": response.get("success_prediction", {}).get("success_probability", ""),
        "missing_count": len(response.get("intake", {}).get("missing_questions") or []),
        "claim_items": claim_names[:4],
        "suggested_documents": response.get("suggested_documents", [])[:4],
        "keyword_hit": keyword_hit,
    }


def run_matrix() -> Dict[str, Any]:
    client = TestClient(create_app())
    rows = []
    failures = []

    for index, case in enumerate(build_cases(), start=1):
        payload = case["request"]
        try:
            res = client.post("/arbitration/workup", json=payload)
            if res.status_code != 200:
                row = {
                    "index": index,
                    "identity": case["identity"],
                    "input_case_type": payload["case_type"],
                    "status": "FAIL",
                    "error": res.text[:500],
                }
            else:
                row = summarize_case(index, case, payload, res.json())
        except Exception as exc:
            row = {
                "index": index,
                "identity": case["identity"],
                "input_case_type": payload["case_type"],
                "status": "FAIL",
                "error": f"{type(exc).__name__}: {exc}",
            }
        rows.append(row)
        if row["status"] != "PASS":
            failures.append(row)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total": len(rows),
        "pass_count": sum(1 for row in rows if row["status"] == "PASS"),
        "check_count": sum(1 for row in rows if row["status"] == "CHECK"),
        "fail_count": sum(1 for row in rows if row["status"] == "FAIL"),
        "rows": rows,
        "failures": failures,
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# 劳动仲裁 20 案例后端稳定性报告",
        "",
        f"- 生成时间：{report['generated_at']}",
        f"- 总案例：{report['total']}",
        f"- 通过：{report['pass_count']}",
        f"- 需复核：{report['check_count']}",
        f"- 失败：{report['fail_count']}",
        "",
        "| # | 身份 | 输入类型 | 状态 | 阶段 | 风险 | 把握 | 缺口 | 识别诉求 | 建议材料 |",
        "|---|---|---|---|---|---|---|---:|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {index} | {identity} | {input_case_type} | {status} | {workflow_stage} | {risk_level} | {success_probability} | {missing_count} | {claims} | {docs} |".format(
                **row,
                claims=" / ".join(row.get("claim_items", [])) or "-",
                docs=" / ".join(row.get("suggested_documents", [])) or "-",
            )
        )
    if report["failures"]:
        lines.extend(["", "## 需处理项", ""])
        for row in report["failures"]:
            lines.append(f"- #{row['index']} {row['identity']}：{row['status']} {row.get('error', '')}")
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = run_matrix()
    (OUTPUT_DIR / "case_matrix_latest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown = render_markdown(report)
    (OUTPUT_DIR / "case_matrix_latest.md").write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
