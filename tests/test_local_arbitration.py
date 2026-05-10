import asyncio
import os
import unittest
import uuid

os.environ.setdefault("LLM_PROVIDER", "local")
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/runtime/test_lerap_app.db")

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.services.arbitration_analyzer import ArbitrationAnalyzer
from app.services.arbitration_document_generator import ArbitrationDocumentGenerator, DocumentType
from app.services.chongqing_calculator import ChongqingLaborCalculator
from app.services.legal_workflow import LegalWorkflowAnalyzer
from app.services.llm_client import LLMClient
from app.services.rag_retriever import retrieve_context


def sample_case():
    return {
        "case_type": "工资报酬纠纷",
        "facts": "申请人自2023年起在重庆某科技公司工作，2025年2月至4月公司拖欠工资三个月，且未支付加班费。申请人有劳动合同、工资流水和聊天记录。",
        "evidence": ["劳动合同", "工资流水", "聊天记录"],
        "applicant_info": {
            "name": "张三",
            "employer_name": "重庆某科技公司",
            "start_date": "2023-03-01",
            "salary": 12000,
        },
        "evidence_quality": "良好",
        "applicant_background": "普通员工",
        "salary": 12000,
        "years": 2.2,
    }


class LocalArbitrationTests(unittest.TestCase):
    def test_root_serves_frontend_workbench(self):
        client = TestClient(create_app())
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("L-ERAP PRO", response.text)
        self.assertIn("当前会话", response.text)

    def test_auth_and_workspace_persist_on_server(self):
        client = TestClient(create_app())
        email = f"worker-{uuid.uuid4().hex[:8]}@example.com"

        register_res = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "Password123",
                "full_name": "测试用户",
                "role": "案件申请人",
            },
        )
        self.assertEqual(register_res.status_code, 201)
        self.assertIn("lerap_session", register_res.headers.get("set-cookie", ""))

        me_res = client.get("/auth/me")
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["user"]["email"], email)

        profile_res = client.put(
            "/auth/profile",
            json={
                "full_name": "新测试用户",
                "role": "劳动者",
            },
        )
        self.assertEqual(profile_res.status_code, 200)
        self.assertEqual(profile_res.json()["user"]["full_name"], "新测试用户")
        self.assertEqual(profile_res.json()["user"]["role"], "劳动者")

        change_password_res = client.post(
            "/auth/change-password",
            json={
                "current_password": "Password123",
                "new_password": "NewPass456",
            },
        )
        self.assertEqual(change_password_res.status_code, 200)

        logout_after_change = client.post("/auth/logout")
        self.assertEqual(logout_after_change.status_code, 204)

        login_with_old_password = client.post(
            "/auth/login",
            json={"email": email, "password": "Password123"},
        )
        self.assertEqual(login_with_old_password.status_code, 401)

        login_with_new_password = client.post(
            "/auth/login",
            json={"email": email, "password": "NewPass456"},
        )
        self.assertEqual(login_with_new_password.status_code, 200)

        import_res = client.post(
            "/workspace/import-legacy",
            json={
                "history_entries": [
                    {
                        "title": "旧版工资案件",
                        "kindLabel": "案情整理",
                        "readiness": "补充事实和证据",
                        "primaryFinding": "旧版主结论",
                        "nextBestAction": "旧版下一步",
                        "caseForm": {
                            "facts": sample_case()["facts"],
                            "goal": "旧版导入",
                            "years": 2.2,
                            "contact_phone": "13900000000",
                            "applicant_info": {
                                "name": "张三",
                                "employer_name": "重庆某科技公司",
                                "workplace": "重庆市渝北区",
                                "salary": 12000,
                            },
                        },
                        "evidenceText": "劳动合同\n工资流水",
                        "documentResult": {"document_type": "仲裁申请书", "content": "旧版草稿"},
                        "documentValidation": {"is_valid": True, "issues": [], "warnings": [], "suggestions": []},
                    }
                ],
                "activities": [
                    {"title": "旧版动作", "detail": "浏览器本地记录迁移测试"}
                ],
            },
        )
        self.assertEqual(import_res.status_code, 200)
        self.assertEqual(import_res.json()["imported_cases"], 1)
        self.assertEqual(import_res.json()["imported_activities"], 1)

        save_res = client.post(
            "/workspace/cases",
            json={
                "title": "工资报酬纠纷 · 重庆某科技公司",
                "case_type": "工资报酬纠纷",
                "primary_finding": "建议先补强工资流水和考勤。",
                "readiness": "补充事实和证据",
                "next_best_action": "生成仲裁申请书",
                "snapshot": {
                    "title": "工资报酬纠纷 · 重庆某科技公司",
                    "caseForm": {
                        "facts": sample_case()["facts"],
                        "goal": "追回拖欠工资并准备仲裁申请书",
                        "years": 2.2,
                        "contact_phone": "13800000000",
                        "applicant_info": {
                            "name": "张三",
                            "employer_name": "重庆某科技公司",
                            "workplace": "重庆市渝北区",
                            "salary": 12000,
                        },
                    },
                    "evidenceText": "劳动合同\n工资流水\n聊天记录",
                    "documentType": "仲裁申请书",
                    "workupResult": {"workflow_stage": "补充事实和证据"},
                    "documentResult": {"content": "劳动仲裁申请书草稿"},
                },
            },
        )
        self.assertEqual(save_res.status_code, 200)
        case_payload = save_res.json()
        case_id = case_payload["id"]
        self.assertEqual(case_payload["title"], "工资报酬纠纷 · 重庆某科技公司")

        list_res = client.get("/workspace/cases")
        self.assertEqual(list_res.status_code, 200)
        self.assertTrue(any(item["id"] == case_id for item in list_res.json()["items"]))

        detail_res = client.get(f"/workspace/cases/{case_id}")
        self.assertEqual(detail_res.status_code, 200)
        self.assertEqual(detail_res.json()["snapshot"]["documentType"], "仲裁申请书")

        activities_res = client.get("/workspace/activities")
        self.assertEqual(activities_res.status_code, 200)
        self.assertTrue(activities_res.json()["items"])

        delete_res = client.delete(f"/workspace/cases/{case_id}")
        self.assertEqual(delete_res.status_code, 204)

        logout_res = client.post("/auth/logout")
        self.assertEqual(logout_res.status_code, 204)

        me_after_logout = client.get("/auth/me")
        self.assertEqual(me_after_logout.status_code, 401)

    def test_llm_local_mode_basic(self):
        client = LLMClient()

        async def _run():
            self.assertEqual(await client.classify_intent("帮我生成仲裁申请书"), "draft")
            draft = await client.generate_draft("帮我分析", "query", ["重庆劳动仲裁"])
            self.assertTrue("本地模式" in draft or "补充" in draft)
            ok, errors, final_output = await client.audit_compliance("请补充案件事实后再提交。", [])
            self.assertFalse(ok)
            self.assertTrue(errors)
            self.assertTrue(final_output)

        asyncio.run(_run())

    def test_analyzer_and_documents_work_locally(self):
        async def _run():
            analyzer = ArbitrationAnalyzer()
            case = sample_case()
            analysis = await analyzer.analyze_case(case)
            self.assertEqual(analysis.case_type, case["case_type"])
            self.assertIn(analysis.risk_level.value, {"低风险", "中风险", "高风险"})
            self.assertTrue(analysis.missing_info is None or isinstance(analysis.missing_info, list))
            self.assertIsInstance(analysis.jurisdiction, dict)
            self.assertIsInstance(analysis.limitation, dict)
            self.assertTrue(analysis.claim_items)
            self.assertTrue(analysis.evidence_checklist)
            self.assertTrue(analysis.action_plan)
            self.assertIsInstance(analysis.local_reference, dict)

            cost = await analyzer.estimate_cost(case)
            self.assertGreaterEqual(cost["total_cost"], cost["arbitration_fee"])
            self.assertEqual(cost["arbitration_fee"], 0.0)

            prediction = await analyzer.predict_success_rate(case)
            self.assertIn("success_probability", prediction)

            generator = ArbitrationDocumentGenerator()
            doc = await generator.generate_arbitration_document(DocumentType.ARBITRATION_APPLICATION, case)
            self.assertIn("劳动仲裁申请书", doc)
            mediation = await generator.generate_arbitration_document(DocumentType.MEDIATION_APPLICATION, case)
            self.assertIn("庭前调解申请书", mediation)

        asyncio.run(_run())

    def test_api_contract_fields_match_frontend_expectations(self):
        client = TestClient(create_app())
        case = sample_case()

        analyze_res = client.post("/arbitration/analyze", json=case)
        self.assertEqual(analyze_res.status_code, 200)
        payload = analyze_res.json()
        self.assertIn("analysis", payload)
        self.assertIn("summary", payload["analysis"])
        self.assertIn("jurisdiction", payload)
        self.assertIn("limitation", payload)
        self.assertIn("claim_items", payload)
        self.assertIn("evidence_checklist", payload)
        self.assertIn("action_plan", payload)
        self.assertIn("local_reference", payload)

        cost_res = client.post("/arbitration/estimate-cost", json=case)
        self.assertEqual(cost_res.status_code, 200)
        cost_payload = cost_res.json()
        self.assertIn("cost_estimate", cost_payload)
        self.assertIn("explanation", cost_payload)

        success_res = client.post("/arbitration/predict-success-rate", json=case)
        self.assertEqual(success_res.status_code, 200)
        success_payload = success_res.json()
        self.assertIn("success_rate", success_payload)
        self.assertIn("explanation", success_payload)

        doc_res = client.post(
            "/arbitration/generate-document",
            json={"document_type": "仲裁申请书", "case_data": case},
        )
        self.assertEqual(doc_res.status_code, 200)
        doc_payload = doc_res.json()
        self.assertIn("advice", doc_payload)
        self.assertIn("document", doc_payload)

        mediation_res = client.post(
            "/arbitration/generate-document",
            json={"document_type": "庭前调解申请书", "case_data": case},
        )
        self.assertEqual(mediation_res.status_code, 200)
        self.assertIn("庭前调解申请书", mediation_res.json()["content"])

        validate_res = client.post(
            "/arbitration/validate-document",
            json={
                "document_type": "仲裁申请书",
                "case_data": case,
                "content": doc_payload["content"],
            },
        )
        self.assertEqual(validate_res.status_code, 200)
        validate_payload = validate_res.json()
        self.assertIn("is_valid", validate_payload)
        self.assertIn("warnings", validate_payload)

        calc_res = client.post(
            "/arbitration/calculate-claim",
            json={"calculation_type": "违法解除", "salary": 10000, "years": 2.2, "reason": "违法解除"},
        )
        self.assertEqual(calc_res.status_code, 200)
        calc_payload = calc_res.json()
        self.assertEqual(calc_payload["amount"], 50000)
        self.assertIn("formula", calc_payload)

        intake_res = client.post(
            "/arbitration/intake-checklist",
            json={"case_type": "加班费纠纷", "facts": "重庆公司长期安排加班", "evidence": [], "applicant_info": {}},
        )
        self.assertEqual(intake_res.status_code, 200)
        intake_payload = intake_res.json()
        self.assertIn("missing_questions", intake_payload)
        self.assertIn("evidence_checklist", intake_payload)

        refs_res = client.get(
            "/arbitration/local-references",
            params={"query": "重庆 调岗 工作地点 违法解除", "limit": 3},
        )
        self.assertEqual(refs_res.status_code, 200)
        refs_payload = refs_res.json()
        self.assertTrue(refs_payload["references"])

        workup_res = client.post("/arbitration/workup", json=case)
        self.assertEqual(workup_res.status_code, 200)
        workup_payload = workup_res.json()
        self.assertIn("analysis", workup_payload)
        self.assertIn("intake", workup_payload)
        self.assertIn("local_references", workup_payload)
        self.assertIn("suggested_documents", workup_payload)
        self.assertIn("service_recommendation", workup_payload)
        self.assertIn("compliance_notes", workup_payload["service_recommendation"])
        self.assertIn("pipeline_status", workup_payload)
        self.assertTrue(workup_payload["pipeline_status"])
        self.assertTrue(any(step["name"] == "case_analysis" for step in workup_payload["pipeline_status"]))
        review = workup_payload["analysis"].get("opposition_review") or {}
        self.assertIn("agent_result", review.get("red_lawyer_analysis", {}))
        self.assertIn("agent_result", review.get("blue_lawyer_analysis", {}))

    def test_rag_retrieval_returns_context_or_fallback(self):
        result = retrieve_context("重庆 劳动法 工资 拖欠", top_k=2)
        self.assertIsInstance(result, list)

    def test_rag_prioritizes_chongqing_local_sources(self):
        result = retrieve_context("重庆 主播 劳动关系 新就业形态", top_k=2)
        self.assertTrue(result)
        joined = "\n".join(result)
        self.assertIn("重庆", joined)
        self.assertTrue("新就业形态" in joined or "主播" in joined)

    def test_workflow_handles_jurisdiction_limitation_and_claims(self):
        analyzer = LegalWorkflowAnalyzer()
        result = analyzer.analyze(sample_case())
        self.assertTrue(result.jurisdiction["is_labor_dispute"])
        self.assertTrue(any(item["name"] == "拖欠工资/劳动报酬" for item in result.claim_items))
        self.assertTrue(result.legal_basis)

    def test_workflow_recognizes_annual_leave_wage_claim(self):
        analyzer = LegalWorkflowAnalyzer()
        case = sample_case()
        case["case_type"] = "未休年假工资纠纷"
        case["facts"] = "工作三年从未安排年休假，离职时也没有折算未休年休假工资。"
        result = analyzer.analyze(case)
        claim_names = [item["name"] for item in result.claim_items]
        self.assertIn("未休年休假工资", claim_names)
        self.assertNotIn("拖欠工资/劳动报酬", claim_names)

    def test_severance_year_normalization(self):
        self.assertEqual(ChongqingLaborCalculator.normalize_service_years(2.2), 2.5)
        self.assertEqual(ChongqingLaborCalculator.normalize_service_years(2.6), 3.0)
        self.assertEqual(ChongqingLaborCalculator.calculate_severance(10000, 2.2, "合法解除"), 25000)


if __name__ == "__main__":
    unittest.main()
