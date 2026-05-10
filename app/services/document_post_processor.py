"""
文书后处理校验管线

在文书生成后对内容进行多维度校验，发现格式错误、
信息缺失和逻辑不一致等问题，返回结构化的校验报告。
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class DocumentCheckResult:
    check_name: str
    passed: bool
    message: str = ""
    severity: str = "warning"  # "error" | "warning" | "info"


@dataclass
class PostProcessorReport:
    document_type: str
    is_valid: bool
    checks: List[DocumentCheckResult] = field(default_factory=list)
    auto_fixes_applied: List[str] = field(default_factory=list)

    @property
    def errors(self) -> List[str]:
        return [c.message for c in self.checks if not c.passed and c.severity == "error"]

    @property
    def warnings(self) -> List[str]:
        return [c.message for c in self.checks if not c.passed and c.severity == "warning"]


# 中文法条引用格式：《XXX》第X条
_LAW_CITATION_PATTERN = re.compile(r"《[^》]+》第?\d+条?")

# 日期格式：应为 YYYY年MM月DD日
_DATE_PATTERN_CORRECT = re.compile(r"\d{4}年\d{1,2}月\d{1,2}日")
_DATE_PATTERN_WRONG = re.compile(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}")

# 占位符残留
_PLACEHOLDER_PATTERNS = [
    re.compile(r"【[^】]*待补充[^】]*】"),
    re.compile(r"______"),
    re.compile(r"\[待填写\]"),
    re.compile(r"(?<![A-Za-z0-9])XXX(?![A-Za-z0-9])"),
]


class DocumentPostProcessor:
    """文书后处理校验器"""

    def validate(
        self,
        content: str,
        document_type: str,
        case_data: Dict[str, Any],
    ) -> PostProcessorReport:
        checks = [
            self._check_party_names(content, case_data),
            self._check_amount_consistency(content, case_data),
            self._check_date_format(content),
            self._check_legal_citations(content),
            self._check_placeholder_leaked(content),
            self._check_content_length(content, document_type),
        ]

        is_valid = not any(
            not c.passed and c.severity == "error" for c in checks
        )

        return PostProcessorReport(
            document_type=document_type,
            is_valid=is_valid,
            checks=checks,
        )

    def _check_party_names(
        self, content: str, case_data: Dict[str, Any]
    ) -> DocumentCheckResult:
        applicant_info = case_data.get("applicant_info") or {}
        applicant_name = str(applicant_info.get("name") or "").strip()
        employer_name = str(applicant_info.get("employer_name") or "").strip()

        missing = []
        if applicant_name and applicant_name not in content:
            missing.append(f"申请人「{applicant_name}」")
        if employer_name and employer_name not in content:
            missing.append(f"被申请人「{employer_name}」")

        if missing:
            return DocumentCheckResult(
                check_name="party_names",
                passed=False,
                message=f"文书中未出现：{'、'.join(missing)}",
                severity="error",
            )
        return DocumentCheckResult(check_name="party_names", passed=True)

    def _check_amount_consistency(
        self, content: str, case_data: Dict[str, Any]
    ) -> DocumentCheckResult:
        amounts_to_check = []
        salary = case_data.get("salary") or (case_data.get("applicant_info") or {}).get("salary")
        amount = case_data.get("amount")

        if salary:
            amounts_to_check.append(("工资基数", salary))
        if amount:
            amounts_to_check.append(("请求金额", amount))

        missing = []
        for label, value in amounts_to_check:
            try:
                num = float(value)
                int_str = str(int(num))
                float_str = f"{num:.2f}"
                if int_str not in content and float_str not in content and str(value) not in content:
                    missing.append(label)
            except (TypeError, ValueError):
                pass

        if missing:
            return DocumentCheckResult(
                check_name="amount_consistency",
                passed=False,
                message=f"以下金额未在文书中出现：{'、'.join(missing)}，请核对。",
                severity="warning",
            )
        return DocumentCheckResult(check_name="amount_consistency", passed=True)

    def _check_date_format(self, content: str) -> DocumentCheckResult:
        wrong_dates = _DATE_PATTERN_WRONG.findall(content)
        if wrong_dates:
            return DocumentCheckResult(
                check_name="date_format",
                passed=False,
                message=f"发现非标准日期格式（应为YYYY年MM月DD日）：{wrong_dates[:3]}",
                severity="warning",
            )
        return DocumentCheckResult(check_name="date_format", passed=True)

    def _check_legal_citations(self, content: str) -> DocumentCheckResult:
        citations = _LAW_CITATION_PATTERN.findall(content)
        if not citations:
            return DocumentCheckResult(
                check_name="legal_citations",
                passed=False,
                message="文书中未发现法条引用（如《劳动合同法》第X条），建议补充法律依据。",
                severity="warning",
            )
        return DocumentCheckResult(check_name="legal_citations", passed=True)

    def _check_placeholder_leaked(self, content: str) -> DocumentCheckResult:
        found = []
        for pattern in _PLACEHOLDER_PATTERNS:
            matches = pattern.findall(content)
            found.extend(matches)

        if found:
            return DocumentCheckResult(
                check_name="placeholder_leaked",
                passed=False,
                message=f"文书中存在未填写的占位符：{found[:5]}",
                severity="error",
            )
        return DocumentCheckResult(check_name="placeholder_leaked", passed=True)

    def _check_content_length(
        self, content: str, document_type: str
    ) -> DocumentCheckResult:
        min_lengths = {
            "仲裁申请书": 200,
            "庭前调解申请书": 100,
            "答辩书": 150,
            "证据清单": 50,
            "代理词": 200,
        }
        min_len = min_lengths.get(document_type, 50)
        if len(content) < min_len:
            return DocumentCheckResult(
                check_name="content_length",
                passed=False,
                message=f"{document_type}内容过短（{len(content)}字），可能生成不完整。",
                severity="error",
            )
        return DocumentCheckResult(check_name="content_length", passed=True)
