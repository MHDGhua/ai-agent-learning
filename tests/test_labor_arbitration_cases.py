import asyncio
import os
import unittest
from datetime import date

os.environ.setdefault("LLM_PROVIDER", "local")

from app.services.arbitration_document_generator import ArbitrationDocumentGenerator, DocumentType
from app.services.arbitration_analyzer import ArbitrationAnalyzer
from app.services.chongqing_calculator import ChongqingLaborCalculator
from app.services.legal_workflow import LegalWorkflowAnalyzer, STABLE_LEGAL_BASIS


FIXED_TODAY = date(2026, 5, 10)


def make_case(
    *,
    case_type,
    facts,
    evidence=None,
    applicant_info=None,
    salary=12000,
    years=2.2,
    evidence_quality="良好",
    applicant_background="普通员工",
    dispute_date=None,
    termination_date=None,
    still_employed=False,
    amount=18000,
):
    data = {
        "case_type": case_type,
        "facts": facts,
        "evidence": evidence or [],
        "applicant_info": {
            "name": "张三",
            "employer_name": "重庆某科技公司",
            "start_date": "2023-03-01",
            "salary": salary,
            "workplace": "重庆市渝北区",
            "employer_address": "重庆市渝北区xx路1号",
        },
        "evidence_quality": evidence_quality,
        "applicant_background": applicant_background,
        "salary": salary,
        "years": years,
        "amount": amount,
    }
    if applicant_info:
        data["applicant_info"].update(applicant_info)
    if dispute_date:
        data["applicant_info"]["dispute_date"] = dispute_date
    if termination_date:
        data["applicant_info"]["termination_date"] = termination_date
    if still_employed:
        data["applicant_info"]["still_employed"] = True
    return data


def claim_names(result):
    return [item["name"] for item in result.claim_items]


class LaborArbitrationScenarioTests(unittest.TestCase):
    def setUp(self):
        self.workflow = LegalWorkflowAnalyzer()
        self.generator = ArbitrationDocumentGenerator()
        self.analyzer = ArbitrationAnalyzer()
        self.calculator = ChongqingLaborCalculator()

    def test_twenty_typical_labor_arbitration_scenarios(self):
        async def _run():
            scenarios = [
                {
                    "name": "拖欠工资申请",
                    "kind": "workflow_doc",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="申请人自2023年起在重庆工作，2025年2月至4月公司连续拖欠工资三个月，并拖欠未结算的劳动报酬。",
                        evidence=["劳动合同", "工资流水", "聊天记录"],
                    ),
                    "claim": "拖欠工资/劳动报酬",
                    "document_type": DocumentType.ARBITRATION_APPLICATION,
                    "document_contains": "拖欠工资",
                },
                {
                    "name": "加班费争议",
                    "kind": "workflow_evidence",
                    "case": make_case(
                        case_type="加班费纠纷",
                        facts="公司长期安排周末加班且未支付休息日和法定节假日加班费，考勤与工作群记录均可印证。",
                        evidence=["考勤记录", "工作群通知", "排班表"],
                    ),
                    "claim": "加班费",
                    "evidence_category": "加班事实",
                },
                {
                    "name": "违法解除赔偿",
                    "kind": "workflow_basis",
                    "case": make_case(
                        case_type="违法解除劳动合同纠纷",
                        facts="用人单位未说明理由直接辞退申请人，解除通知与沟通录音可以证明属于违法解除劳动合同。",
                        evidence=["解除通知", "谈话录音", "工资流水"],
                    ),
                    "claim": "违法解除赔偿金或经济补偿金",
                    "basis": STABLE_LEGAL_BASIS["burden"],
                },
                {
                    "name": "未签合同双倍工资",
                    "kind": "workflow_doc",
                    "case": make_case(
                        case_type="未签书面劳动合同争议",
                        facts="申请人入职后始终未签书面劳动合同，已满一个月仍未补签，要求支付二倍工资差额。",
                        evidence=["入职登记表", "工资流水"],
                    ),
                    "claim": "未签书面劳动合同二倍工资差额",
                    "document_type": DocumentType.ARBITRATION_APPLICATION,
                    "document_contains": "二倍工资差额",
                },
                {
                    "name": "工伤待遇争议",
                    "kind": "workflow_evidence",
                    "case": make_case(
                        case_type="工伤待遇争议",
                        facts="申请人在工作中受伤后送医治疗，现主张工伤待遇和相应赔偿。",
                        evidence=["事故经过说明", "诊断证明", "就医记录"],
                    ),
                    "claim": "工伤待遇",
                    "evidence_category": "工伤事实",
                },
                {
                    "name": "社保争议",
                    "kind": "workflow_claim",
                    "case": make_case(
                        case_type="社保争议",
                        facts="公司长期未依法缴纳社会保险，申请人据此主张社保相关处理。",
                        evidence=["工资流水", "社保缴费记录"],
                    ),
                    "claim": "社会保险相关处理",
                },
                {
                    "name": "劳动关系确认",
                    "kind": "workflow_claim",
                    "case": make_case(
                        case_type="确认劳动关系纠纷",
                        facts="申请人主张与被申请人之间存在劳动关系，请求先确认基础劳动关系。",
                        evidence=["工作证"],
                    ),
                    "claim": "确认劳动关系/基础劳动争议请求",
                },
                {
                    "name": "在职欠薪时效",
                    "kind": "limitation_status",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="公司拖欠工资，但劳动关系仍在存续，申请人持续催要未果。",
                        evidence=["工资流水", "聊天记录"],
                        dispute_date="2026-04-01",
                        still_employed=True,
                    ),
                    "status": "wage_claim_during_employment",
                },
                {
                    "name": "离职后欠薪未过期",
                    "kind": "limitation_status",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="申请人于离职后主张此前拖欠的工资报酬，现距离争议发生未满一年。",
                        evidence=["工资流水", "离职交接记录"],
                        dispute_date="2025-08-01",
                        termination_date="2025-08-01",
                    ),
                    "status": "within_period",
                    "special_note": "终止后",
                },
                {
                    "name": "离职后欠薪可能过期",
                    "kind": "limitation_warning",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="申请人在劳动关系终止后很久才主张工资报酬，需重点核查时效。",
                        evidence=["工资流水"],
                        dispute_date="2024-12-01",
                        termination_date="2024-12-01",
                    ),
                    "status": "possibly_expired",
                    "warning": "可能超过一年仲裁时效",
                },
                {
                    "name": "重庆管辖明确",
                    "kind": "jurisdiction",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="申请人在重庆市渝北区工作，劳动合同履行地明确，仲裁管辖线索清晰。",
                        evidence=["劳动合同"],
                        applicant_info={
                            "workplace": "重庆市渝北区",
                            "contract_place": "重庆市渝北区",
                            "employer_address": "重庆市渝北区xx路1号",
                        },
                    ),
                    "expected_true": True,
                },
                {
                    "name": "管辖信息缺失",
                    "kind": "jurisdiction_missing",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="申请人只描述了争议概况，未提供用人单位地址和实际工作地。",
                        evidence=["聊天记录"],
                        applicant_info={
                            "name": "张三",
                            "employer_name": "",
                            "workplace": "",
                            "contract_place": "",
                            "employer_address": "",
                        },
                    ),
                    "missing": {
                        "用人单位全称",
                        "实际工作地或劳动合同履行地",
                        "用人单位注册地址或办公地址",
                    },
                },
                {
                    "name": "证据部分齐备",
                    "kind": "evidence_partial",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="劳动合同和工资流水已找到，部分基础证据已具备。",
                        evidence=["劳动合同", "工资流水", "聊天记录"],
                    ),
                    "expected_status": "partially_ready",
                },
                {
                    "name": "证据为空",
                    "kind": "evidence_empty",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="申请人只记得大概经过，但尚未整理任何证据。",
                        evidence=[],
                    ),
                    "warning": "证据为空",
                },
                {
                    "name": "高胜率",
                    "kind": "success_high",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="证据充分，劳动合同、工资流水、聊天记录、考勤表和录音均已保存。",
                        evidence=["劳动合同", "工资流水", "聊天记录", "考勤记录", "录音"],
                        evidence_quality="优秀",
                        applicant_background="特殊群体",
                    ),
                },
                {
                    "name": "低胜率",
                    "kind": "success_low",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="申请人仅有一张模糊照片，其他关键事实缺少佐证。",
                        evidence=["模糊照片"],
                        evidence_quality="较差",
                        applicant_background="管理层",
                    ),
                },
                {
                    "name": "仲裁申请书",
                    "kind": "document",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="公司拖欠工资并拖欠加班费，现申请仲裁。",
                        evidence=["劳动合同", "工资流水"],
                    ),
                    "document_type": DocumentType.ARBITRATION_APPLICATION,
                    "contains": ["劳动仲裁申请书", "拖欠工资", "重庆市______区劳动人事争议仲裁委员会"],
                },
                {
                    "name": "答辩书",
                    "kind": "document",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="被申请人认为不存在拖欠工资及加班费问题，现提交答辩意见。",
                        evidence=["劳动合同"],
                    ),
                    "document_type": DocumentType.DEFENSE_RESPONSE,
                    "contains": ["劳动仲裁答辩书", "被申请人", "劳动争议一案"],
                },
                {
                    "name": "证据清单",
                    "kind": "document",
                    "case": make_case(
                        case_type="工资报酬纠纷",
                        facts="证据清单中列明劳动合同、工资流水和聊天记录。",
                        evidence=["劳动合同", "工资流水", "聊天记录"],
                    ),
                    "document_type": DocumentType.EVIDENCE_LIST,
                    "contains": ["证据清单", "劳动合同", "工资流水", "聊天记录"],
                },
                {
                    "name": "经济补偿计算",
                    "kind": "calc",
                    "salary": 50000,
                    "years": 3,
                    "reason": "违法解除",
                    "expected": 141300.0,
                },
            ]

            for scenario in scenarios:
                with self.subTest(scenario=scenario["name"]):
                    if scenario["kind"] in {"workflow_doc", "workflow_evidence", "workflow_basis", "workflow_claim", "limitation_status", "limitation_warning", "jurisdiction", "jurisdiction_missing", "evidence_partial", "evidence_empty"}:
                        result = self.workflow.analyze(scenario["case"], today=FIXED_TODAY)

                    if scenario["kind"] == "workflow_doc":
                        self.assertIn(scenario["claim"], claim_names(result))
                        content = await self.generator.generate_arbitration_document(
                            scenario["document_type"], scenario["case"]
                        )
                        self.assertIn(scenario["document_contains"], content)
                    elif scenario["kind"] == "workflow_evidence":
                        self.assertIn(scenario["claim"], claim_names(result))
                        self.assertTrue(
                            any(item["category"] == scenario["evidence_category"] and item["status"] == "partially_ready" for item in result.evidence_checklist)
                        )
                    elif scenario["kind"] == "workflow_basis":
                        self.assertIn(scenario["claim"], claim_names(result))
                        self.assertIn(scenario["basis"], result.legal_basis)
                    elif scenario["kind"] == "workflow_claim":
                        self.assertIn(scenario["claim"], claim_names(result))
                    elif scenario["kind"] == "limitation_status":
                        self.assertEqual(result.limitation["status"], scenario["status"])
                        if scenario.get("special_note"):
                            self.assertIn(scenario["special_note"], result.limitation["special_note"])
                    elif scenario["kind"] == "limitation_warning":
                        self.assertEqual(result.limitation["status"], scenario["status"])
                        self.assertTrue(any(scenario["warning"] in item for item in result.warnings))
                    elif scenario["kind"] == "jurisdiction":
                        self.assertTrue(result.jurisdiction["likely_chongqing_jurisdiction"])
                        self.assertIn("重庆", result.jurisdiction["suggested_forum"])
                    elif scenario["kind"] == "jurisdiction_missing":
                        self.assertFalse(result.jurisdiction["likely_chongqing_jurisdiction"])
                        self.assertTrue(set(scenario["missing"]).issubset(set(result.jurisdiction["missing"])))
                    elif scenario["kind"] == "evidence_partial":
                        self.assertTrue(
                            any(item["status"] == scenario["expected_status"] for item in result.evidence_checklist)
                        )
                    elif scenario["kind"] == "evidence_empty":
                        self.assertTrue(any(scenario["warning"] in item for item in result.warnings))
                    elif scenario["kind"] == "success_high":
                        prediction = await self.analyzer.predict_success_rate(scenario["case"])
                        self.assertEqual(prediction["success_probability"], "高")
                        self.assertGreaterEqual(prediction["probability_value"], 0.8)
                    elif scenario["kind"] == "success_low":
                        prediction = await self.analyzer.predict_success_rate(scenario["case"])
                        self.assertEqual(prediction["success_probability"], "低")
                        self.assertLessEqual(prediction["probability_value"], 0.2)
                    elif scenario["kind"] == "document":
                        content = await self.generator.generate_arbitration_document(
                            scenario["document_type"], scenario["case"]
                        )
                        for snippet in scenario["contains"]:
                            self.assertIn(snippet, content)
                    elif scenario["kind"] == "calc":
                        self.assertEqual(
                            self.calculator.normalize_service_years(2.2),
                            2.5,
                        )
                        self.assertEqual(
                            self.calculator.calculate_severance(
                                scenario["salary"], scenario["years"], scenario["reason"]
                            ),
                            scenario["expected"],
                        )

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
