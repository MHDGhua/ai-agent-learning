from typing import TypedDict, List


class AgentState(TypedDict):
    # 外部系统传入的唯一任务标识
    task_id: str
    # 用户的原始输入/提问
    user_input: str
    # 路由层识别出的意图 (如: 'draft', 'audit', 'query')
    intent: str
    # RAG 模块召回的法律条文或案例
    context_data: List[str]
    # Executor 引擎生成的初版结果
    draft_content: str
    # Auditor 节点给出的合规性布尔值
    is_compliant: bool
    # 最终输出给用户或 Callback 的内容
    final_output: str
    # 流转过程中捕获的错误信息
    errors: List[str]

