"""
重庆劳动法赔偿计算引擎（重构版）

基于版本化参数计算经济补偿金、加班费、工伤赔偿，
并通过 CalculationAuditor 对结果进行合规性校验。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from app.knowledge.chongqing_standards import get_standards
from app.core.exceptions import CalculationError


@dataclass
class CalculationResult:
    calculation_type: str
    amount: float
    formula: str
    breakdown: Dict[str, Any] = field(default_factory=dict)
    audit_warnings: List[str] = field(default_factory=list)
    standards_year: str = ""


class ChongqingLaborCalculator:
    """重庆特色劳动法计算引擎"""

    def __init__(self, year: Optional[str] = None):
        self._standards = get_standards(year)
        self.standards_year = year or "2025"

    @property
    def MIN_WAGE(self) -> float:
        return self._standards["min_wage"]

    @property
    def AVG_WAGE(self) -> float:
        return self._standards["avg_wage"]

    @property
    def HIGH_TEMP_ALLOWANCE(self) -> float:
        return self._standards["high_temp_allowance_per_day"]

    @staticmethod
    def normalize_service_years(years: float) -> float:
        """经济补偿年限：不满半年按0.5，满半年不满一年按1。"""
        if years <= 0:
            return 0
        whole_years = int(years)
        remainder = years - whole_years
        if remainder == 0:
            return float(whole_years)
        return whole_years + (0.5 if remainder < 0.5 else 1.0)

    def calculate_severance(
        self,
        salary: float,
        years: float,
        reason: str,
        *,
        pre_2008_years: float = 0.0,
    ) -> float:
        """计算经济补偿金（重庆标准）

        :param salary: 离职前12个月平均工资
        :param years: 总工作年限
        :param reason: 解除原因（合法解除/违法解除）
        :param pre_2008_years: 2008年1月1日前的工龄（用于分段计算）
        :return: 经济补偿金
        """
        if salary < 0 or years < 0:
            raise CalculationError("工资和工龄不能为负数")

        cap_multiplier = self._standards["salary_cap_multiplier"]
        avg_wage = self._standards["avg_wage"]
        year_cap = self._standards["severance_year_cap"]

        capped_salary = min(salary, avg_wage * cap_multiplier)
        is_high_salary = salary > avg_wage * cap_multiplier

        post_2008_years = max(0.0, years - pre_2008_years)
        normalized_post = self.normalize_service_years(post_2008_years)
        normalized_pre = self.normalize_service_years(pre_2008_years)

        # 2008年后部分：高工资受12年上限
        if is_high_salary:
            normalized_post = min(normalized_post, float(year_cap))

        total_months = normalized_pre + normalized_post

        if "违法" in reason:
            return round(capped_salary * total_months * 2, 2)
        return round(capped_salary * total_months, 2)

    def calculate_overtime(self, hours: float, day_type: str, salary: float) -> float:
        """计算加班费（重庆标准）"""
        if hours < 0 or salary < 0:
            raise CalculationError("加班小时数和工资不能为负数")

        pay_days = self._standards["monthly_pay_days"]
        daily_hours = self._standards["daily_hours"]
        hourly_wage = salary / pay_days / daily_hours

        multipliers = {"平日": 1.5, "休息日": 2.0, "节假日": 3.0}
        multiplier = multipliers.get(day_type, 1.5)
        return round(hours * hourly_wage * multiplier, 2)

    def calculate_work_injury(self, level: int, salary: float) -> float:
        """计算一次性伤残补助金"""
        if level < 1 or level > 10:
            raise CalculationError("伤残等级必须在1-10之间")
        if salary < 0:
            raise CalculationError("工资不能为负数")

        coefficients = self._standards["work_injury_disability_months"]
        months = coefficients.get(level, 0)
        return round(salary * months, 2)

    def calculate_work_injury_full(self, level: int, salary: float) -> CalculationResult:
        """计算工伤赔偿完整明细（含医疗补助金和就业补助金）"""
        if level < 1 or level > 10:
            raise CalculationError("伤残等级必须在1-10之间")
        if salary < 0:
            raise CalculationError("工资不能为负数")

        disability_months = self._standards["work_injury_disability_months"]
        medical_months = self._standards["work_injury_medical_subsidy_months"]
        employment_months = self._standards["work_injury_employment_subsidy_months"]
        social_avg = self._standards["social_avg_wage"]

        disability_amount = salary * disability_months.get(level, 0)

        # 5-10级解除/终止劳动关系时才有医疗和就业补助金
        medical_amount = 0.0
        employment_amount = 0.0
        if level >= 5:
            medical_amount = social_avg * medical_months.get(level, 0)
            employment_amount = social_avg * employment_months.get(level, 0)

        total = disability_amount + medical_amount + employment_amount

        return CalculationResult(
            calculation_type="work_injury_full",
            amount=round(total, 2),
            formula="一次性伤残补助金 + 一次性工伤医疗补助金 + 一次性伤残就业补助金",
            breakdown={
                "disability_allowance": round(disability_amount, 2),
                "disability_months": disability_months.get(level, 0),
                "medical_subsidy": round(medical_amount, 2),
                "medical_months": medical_months.get(level, 0),
                "employment_subsidy": round(employment_amount, 2),
                "employment_months": employment_months.get(level, 0),
                "base_salary": salary,
                "social_avg_wage": social_avg,
                "injury_level": level,
            },
            standards_year=self.standards_year,
        )


class CalculationAuditor:
    """对赔偿计算结果进行合规性校验"""

    def __init__(self, year: Optional[str] = None):
        self._standards = get_standards(year)

    def audit_severance(
        self,
        salary: float,
        years: float,
        result_amount: float,
        reason: str,
        pre_2008_years: float = 0.0,
    ) -> List[str]:
        warnings = []
        avg_wage = self._standards["avg_wage"]
        cap = avg_wage * self._standards["salary_cap_multiplier"]

        if salary > cap:
            warnings.append(
                f"月工资 {salary:.0f} 元超过社平工资3倍（{cap:.0f} 元），已按上限计算。"
            )

        post_2008 = years - pre_2008_years
        if salary > cap and post_2008 > 12:
            warnings.append(
                "高工资且2008年后工龄超12年，补偿月数已按12个月封顶。"
            )

        if years > 20:
            warnings.append("工龄超过20年，请确认入职时间和劳动关系连续性。")

        if "违法" in reason and result_amount > cap * 24:
            warnings.append("违法解除赔偿金较高，建议核实解除事实和程序。")

        return warnings

    def audit_overtime(self, hours: float, day_type: str) -> List[str]:
        warnings = []
        if hours > 36:
            warnings.append("单月加班超36小时，超出法定上限，仲裁委可能不予全额支持。")
        if day_type == "休息日":
            warnings.append("休息日加班应优先安排补休，无法补休才支付2倍工资。")
        return warnings

    def audit_work_injury(self, level: int, salary: float) -> List[str]:
        warnings = []
        min_wage = self._standards["min_wage"]
        if salary < min_wage:
            warnings.append(
                f"工资低于最低工资标准（{min_wage} 元），工伤待遇应按最低工资计算。"
            )
        if level <= 4:
            warnings.append("1-4级伤残保留劳动关系，不适用一次性医疗/就业补助金。")
        return warnings
