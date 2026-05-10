"""
重庆劳动法参数版本化管理

按年度维护最低工资、社平工资、工伤补助系数等参数，
支持按案件发生时间自动选择适用版本。
"""

from typing import Dict, Any, Optional


CHONGQING_STANDARDS: Dict[str, Dict[str, Any]] = {
    "2024": {
        "effective_date": "2024-04-01",
        "min_wage": 2100,
        "avg_wage": 7500,
        "social_avg_wage": 7756,
        "high_temp_allowance_per_day": 25,
        "monthly_pay_days": 21.75,
        "daily_hours": 8,
        "severance_year_cap": 12,
        "salary_cap_multiplier": 3,
        "work_injury_disability_months": {
            1: 27, 2: 25, 3: 23, 4: 21, 5: 18,
            6: 16, 7: 13, 8: 11, 9: 9, 10: 7,
        },
        "work_injury_medical_subsidy_months": {
            5: 18, 6: 16, 7: 14, 8: 12, 9: 10, 10: 8,
        },
        "work_injury_employment_subsidy_months": {
            5: 18, 6: 16, 7: 14, 8: 12, 9: 10, 10: 8,
        },
        "source": "渝人社发〔2024〕相关文件",
    },
    "2025": {
        "effective_date": "2025-04-01",
        "min_wage": 2100,
        "avg_wage": 7850,
        "social_avg_wage": 8100,
        "high_temp_allowance_per_day": 25,
        "monthly_pay_days": 21.75,
        "daily_hours": 8,
        "severance_year_cap": 12,
        "salary_cap_multiplier": 3,
        "work_injury_disability_months": {
            1: 27, 2: 25, 3: 23, 4: 21, 5: 18,
            6: 16, 7: 13, 8: 11, 9: 9, 10: 7,
        },
        "work_injury_medical_subsidy_months": {
            5: 18, 6: 16, 7: 14, 8: 12, 9: 10, 10: 8,
        },
        "work_injury_employment_subsidy_months": {
            5: 18, 6: 16, 7: 14, 8: 12, 9: 10, 10: 8,
        },
        "source": "渝人社发〔2025〕相关文件",
    },
    "2026": {
        "effective_date": "2026-04-01",
        "min_wage": 2100,
        "avg_wage": 7850,
        "social_avg_wage": 8200,
        "high_temp_allowance_per_day": 25,
        "monthly_pay_days": 21.75,
        "daily_hours": 8,
        "severance_year_cap": 12,
        "salary_cap_multiplier": 3,
        "work_injury_disability_months": {
            1: 27, 2: 25, 3: 23, 4: 21, 5: 18,
            6: 16, 7: 13, 8: 11, 9: 9, 10: 7,
        },
        "work_injury_medical_subsidy_months": {
            5: 18, 6: 16, 7: 14, 8: 12, 9: 10, 10: 8,
        },
        "work_injury_employment_subsidy_months": {
            5: 18, 6: 16, 7: 14, 8: 12, 9: 10, 10: 8,
        },
        "source": "渝人社发〔2026〕相关文件（待正式发布后更新）",
    },
}

DEFAULT_YEAR = "2025"


def get_standards(year: Optional[str] = None) -> Dict[str, Any]:
    """获取指定年度的重庆劳动法参数，默认返回最新版本"""
    if year and year in CHONGQING_STANDARDS:
        return CHONGQING_STANDARDS[year]
    return CHONGQING_STANDARDS[DEFAULT_YEAR]


def get_latest_year() -> str:
    return max(CHONGQING_STANDARDS.keys())
