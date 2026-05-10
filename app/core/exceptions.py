"""
L-ERAP-PRO 分层异常体系

所有业务异常继承自 LERAPError，API 层通过 FastAPI exception_handler 统一捕获并返回结构化错误响应。
"""

from typing import Optional


class LERAPError(Exception):
    """系统基础异常"""

    status_code: int = 500
    default_message: str = "系统内部错误，请稍后重试。"

    def __init__(self, message: Optional[str] = None, *, detail: Optional[str] = None):
        self.user_message = message or self.default_message
        self.detail = detail
        super().__init__(self.user_message)


class LLMProviderError(LERAPError):
    """LLM 调用失败（超时、限流、模型不可用）"""

    status_code = 503
    default_message = "AI 分析服务暂时不可用，系统已使用本地规则完成基础分析。"


class KnowledgeBaseError(LERAPError):
    """RAG 检索或知识库访问失败"""

    status_code = 502
    default_message = "知识库检索异常，已使用内置法规完成分析。"


class CalculationError(LERAPError):
    """赔偿计算参数非法或逻辑错误"""

    status_code = 422
    default_message = "计算参数有误，请检查工资、工龄等输入。"


class DocumentGenerationError(LERAPError):
    """文书生成失败"""

    status_code = 422
    default_message = "文书生成失败，请检查案件信息是否完整。"


class CaseValidationError(LERAPError):
    """案件数据校验不通过"""

    status_code = 400
    default_message = "案件信息不完整，请补充必要字段。"
