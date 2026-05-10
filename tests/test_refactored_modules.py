"""
单元测试：重构模块（异常体系、Blackboard、计算器、文书校验）
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("LLM_PROVIDER", "local")


class TestExceptionHierarchy(unittest.TestCase):
    """测试异常体系"""

    def test_lerap_error_defaults(self):
        from app.core.exceptions import LERAPError
        err = LERAPError()
        self.assertEqual(err.status_code, 500)
        self.assertEqual(err.user_message, "系统内部错误，请稍后重试。")

    def test_calculation_error(self):
        from app.core.exceptions import CalculationError
        err = CalculationError("工资不能为负")
        self.assertEqual(err.status_code, 422)
        self.assertEqual(err.user_message, "工资不能为负")

    def test_subclass_relationship(self):
        from app.core.exceptions import LERAPError, LLMProviderError, DocumentGenerationError
        self.assertTrue(issubclass(LLMProviderError, LERAPError))
        self.assertTrue(issubclass(DocumentGenerationError, LERAPError))


class TestBlackboard(unittest.TestCase):
    """测试 Blackboard 共享状态"""

    def test_creation_with_defaults(self):
        from app.core.blackboard import CaseBlackboard, AnalysisStage
        bb = CaseBlackboard(raw_input={"case_type": "劳动纠纷"})
        self.assertEqual(bb.current_stage, AnalysisStage.INTAKE)
        self.assertEqual(len(bb.agent_trace), 0)
        self.assertIsNotNone(bb.case_id)

    def test_record_agent(self):
        from app.core.blackboard import CaseBlackboard, AnalysisStage
        bb = CaseBlackboard()
        bb.record_agent("agent_1", "测试Agent", AnalysisStage.CLASSIFICATION, summary="分类完成")
        self.assertEqual(len(bb.agent_trace), 1)
        self.assertEqual(bb.current_stage, AnalysisStage.CLASSIFICATION)
        self.assertEqual(bb.agent_trace[0].summary, "分类完成")

    def test_set_confidence_clamped(self):
        from app.core.blackboard import CaseBlackboard
        bb = CaseBlackboard()
        bb.set_confidence("agent_1", 1.5)
        self.assertEqual(bb.confidence_scores["agent_1"], 1.0)
        bb.set_confidence("agent_2", -0.3)
        self.assertEqual(bb.confidence_scores["agent_2"], 0.0)

    def test_get_context_for_agent(self):
        from app.core.blackboard import CaseBlackboard, AnalysisStage
        bb = CaseBlackboard(raw_input={"facts": "test"})
        bb.classification = {"case_type": "工伤"}
        bb.workflow_analysis = {"jurisdiction": {}}
        ctx = bb.get_context_for_agent(AnalysisStage.LEGAL_OPINION)
        self.assertIn("classification", ctx)
        self.assertIn("workflow_analysis", ctx)

    def test_to_summary(self):
        from app.core.blackboard import CaseBlackboard, AnalysisStage
        bb = CaseBlackboard()
        bb.record_agent("a1", "A1", AnalysisStage.CLASSIFICATION)
        bb.conflicts = [{"issue": "test"}]
        summary = bb.to_summary()
        self.assertEqual(summary["agents_involved"], 1)
        self.assertEqual(summary["conflicts_count"], 1)


class TestChongqingCalculator(unittest.TestCase):
    """测试赔偿计算器"""

    def setUp(self):
        from app.services.chongqing_calculator import ChongqingLaborCalculator
        self.calc = ChongqingLaborCalculator(year="2025")

    def test_normalize_years_boundary(self):
        self.assertEqual(self.calc.normalize_service_years(0), 0)
        self.assertEqual(self.calc.normalize_service_years(0.3), 0.5)
        self.assertEqual(self.calc.normalize_service_years(0.5), 1.0)
        self.assertEqual(self.calc.normalize_service_years(0.7), 1.0)
        self.assertEqual(self.calc.normalize_service_years(1.0), 1.0)
        self.assertEqual(self.calc.normalize_service_years(3.4), 3.5)
        self.assertEqual(self.calc.normalize_service_years(3.6), 4.0)

    def test_severance_basic(self):
        result = self.calc.calculate_severance(5000, 3, "合法解除")
        self.assertEqual(result, 15000.0)

    def test_severance_illegal(self):
        result = self.calc.calculate_severance(5000, 3, "违法解除")
        self.assertEqual(result, 30000.0)

    def test_severance_salary_cap(self):
        # 3x AVG_WAGE = 23550, salary 30000 should be capped
        result = self.calc.calculate_severance(30000, 1, "合法解除")
        self.assertEqual(result, 23550.0)

    def test_severance_12_year_cap_high_salary(self):
        # High salary + 15 years post-2008 should cap at 12
        result = self.calc.calculate_severance(30000, 15, "合法解除", pre_2008_years=0)
        expected = 23550.0 * 12  # capped salary * 12 months
        self.assertEqual(result, expected)

    def test_severance_pre_2008_split(self):
        # 5 years pre-2008 + 10 years post-2008, high salary
        result = self.calc.calculate_severance(30000, 15, "合法解除", pre_2008_years=5)
        # post-2008: min(10, 12) = 10, pre-2008: 5, total = 15
        expected = 23550.0 * 15
        self.assertEqual(result, expected)

    def test_severance_negative_raises(self):
        from app.core.exceptions import CalculationError
        with self.assertRaises(CalculationError):
            self.calc.calculate_severance(-1000, 3, "合法解除")

    def test_overtime_weekday(self):
        result = self.calc.calculate_overtime(10, "平日", 5000)
        hourly = 5000 / 21.75 / 8
        expected = round(10 * hourly * 1.5, 2)
        self.assertAlmostEqual(result, expected, places=2)

    def test_overtime_holiday(self):
        result = self.calc.calculate_overtime(8, "节假日", 6000)
        hourly = 6000 / 21.75 / 8
        expected = round(8 * hourly * 3, 2)
        self.assertAlmostEqual(result, expected, places=2)

    def test_work_injury_basic(self):
        result = self.calc.calculate_work_injury(10, 5000)
        self.assertEqual(result, 35000.0)

    def test_work_injury_invalid_level(self):
        from app.core.exceptions import CalculationError
        with self.assertRaises(CalculationError):
            self.calc.calculate_work_injury(0, 5000)
        with self.assertRaises(CalculationError):
            self.calc.calculate_work_injury(11, 5000)

    def test_work_injury_full(self):
        result = self.calc.calculate_work_injury_full(7, 6000)
        self.assertGreater(result.amount, 0)
        self.assertIn("disability_allowance", result.breakdown)
        self.assertIn("medical_subsidy", result.breakdown)
        self.assertIn("employment_subsidy", result.breakdown)
        # Level 7: disability=13*6000, medical=14*8100, employment=14*8100
        self.assertEqual(result.breakdown["disability_allowance"], 78000.0)


class TestCalculationAuditor(unittest.TestCase):
    """测试计算审计器"""

    def setUp(self):
        from app.services.chongqing_calculator import CalculationAuditor
        self.auditor = CalculationAuditor(year="2025")

    def test_high_salary_warning(self):
        warnings = self.auditor.audit_severance(30000, 5, 100000, "合法解除")
        self.assertTrue(any("超过社平工资3倍" in w for w in warnings))

    def test_long_service_warning(self):
        warnings = self.auditor.audit_severance(5000, 25, 125000, "合法解除")
        self.assertTrue(any("超过20年" in w for w in warnings))

    def test_overtime_over_36_hours(self):
        warnings = self.auditor.audit_overtime(40, "平日")
        self.assertTrue(any("超36小时" in w for w in warnings))

    def test_work_injury_low_salary(self):
        warnings = self.auditor.audit_work_injury(7, 1500)
        self.assertTrue(any("最低工资" in w for w in warnings))

    def test_work_injury_level_1_4(self):
        warnings = self.auditor.audit_work_injury(3, 8000)
        self.assertTrue(any("1-4级" in w for w in warnings))


class TestDocumentPostProcessor(unittest.TestCase):
    """测试文书后处理校验"""

    def setUp(self):
        from app.services.document_post_processor import DocumentPostProcessor
        self.processor = DocumentPostProcessor()

    def test_valid_document(self):
        content = (
            "劳动仲裁申请书\n\n"
            "申请人：张三，男，汉族，身份证号码：500112199001011234，住址：重庆市渝北区某路某号。\n"
            "被申请人：重庆某公司，统一社会信用代码：91500105MA12345678，住所地：重庆市江北区某路某号。\n\n"
            "仲裁请求：\n"
            "一、请求裁决被申请人支付拖欠工资人民币5000元。\n"
            "二、请求裁决被申请人支付违法解除劳动合同赔偿金。\n\n"
            "事实与理由：\n"
            "申请人于2023年1月1日入职被申请人处，担任技术岗位，月工资5000元。"
            "被申请人于2024年6月30日违法解除劳动合同，未支付任何经济补偿。\n\n"
            "法律依据：依据《劳动合同法》第47条、第87条之规定，被申请人应支付赔偿金。\n\n"
            "此致\n重庆市劳动人事争议仲裁委员会\n\n"
            "申请人：张三\n2024年7月15日"
        )
        case_data = {
            "applicant_info": {"name": "张三", "employer_name": "重庆某公司"},
            "salary": 5000,
        }
        report = self.processor.validate(content, "仲裁申请书", case_data)
        self.assertTrue(report.is_valid)

    def test_missing_party_name(self):
        content = "仲裁申请书\n申请人：李四\n请求支付工资。" * 10
        case_data = {"applicant_info": {"name": "张三", "employer_name": "某公司"}}
        report = self.processor.validate(content, "仲裁申请书", case_data)
        self.assertFalse(report.is_valid)
        self.assertTrue(any("张三" in e for e in report.errors))

    def test_placeholder_detection(self):
        content = "申请人：张三\n被申请人：某公司\n金额：______元\n" + "x" * 200
        case_data = {"applicant_info": {"name": "张三", "employer_name": "某公司"}}
        report = self.processor.validate(content, "仲裁申请书", case_data)
        self.assertFalse(report.is_valid)
        self.assertTrue(any("占位符" in e for e in report.errors))

    def test_wrong_date_format(self):
        content = (
            "申请人：张三\n被申请人：某公司\n"
            "入职日期：2023-01-15\n"
            "依据《劳动合同法》第47条\n" + "x" * 200
        )
        case_data = {"applicant_info": {"name": "张三", "employer_name": "某公司"}}
        report = self.processor.validate(content, "仲裁申请书", case_data)
        self.assertTrue(any("日期格式" in w for w in report.warnings))

    def test_no_legal_citation(self):
        content = "申请人：张三\n被申请人：某公司\n请求支付工资5000元。\n" + "内容" * 100
        case_data = {"applicant_info": {"name": "张三", "employer_name": "某公司"}}
        report = self.processor.validate(content, "仲裁申请书", case_data)
        self.assertTrue(any("法条引用" in w for w in report.warnings))

    def test_short_content(self):
        content = "太短了"
        case_data = {}
        report = self.processor.validate(content, "仲裁申请书", case_data)
        self.assertFalse(report.is_valid)
        self.assertTrue(any("过短" in e for e in report.errors))


class TestChongqingStandards(unittest.TestCase):
    """测试参数版本化"""

    def test_get_default_standards(self):
        from app.knowledge.chongqing_standards import get_standards
        s = get_standards()
        self.assertEqual(s["min_wage"], 2100)
        self.assertEqual(s["avg_wage"], 7850)

    def test_get_specific_year(self):
        from app.knowledge.chongqing_standards import get_standards
        s = get_standards("2024")
        self.assertEqual(s["avg_wage"], 7500)

    def test_fallback_to_default(self):
        from app.knowledge.chongqing_standards import get_standards
        s = get_standards("1999")
        self.assertEqual(s["avg_wage"], 7850)  # falls back to default


if __name__ == "__main__":
    unittest.main()
