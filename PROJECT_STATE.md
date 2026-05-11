# PROJECT_STATE

最后更新：2026-05-11

## 项目定位

L-ERAP-PRO 是面向普通劳动者的重庆劳动仲裁助手，不是专业律师工作台。核心目标是让用户用自然语言描述纠纷，系统完成案情整理、风险提示、红蓝对抗、文书生成和重庆本地参考。

## 当前产品方向

- 主界面以对话区为核心，只展示最关键结论。
- 二级功能放入侧边栏：案情、风险、文书、重庆参考。
- 专业术语要转成普通用户能理解的表达。
- 金额快算作为内部能力使用，不作为独立显眼模块展示。
- 红蓝对抗默认开启。
- 已接入 DeepSeek 官方模型配置，API Key 由用户在 `.env` 自行填写。

## 核心功能边界

- 智能案情分析：多轮引导、法律关系识别、争议焦点提取。
- 仲裁风险评估：红蓝对抗、胜诉把握、调解建议、证据补强。
- 智能文书工厂：仲裁申请书、证据清单、庭前调解申请书、文书防错校验。
- 重庆知识库：重庆本地法规、仲裁委信息、典型案例参考。

## 主要文件地图

- 协作者总览：`docs/status/PROJECT_BRIEF.md`
- 前端入口：`frontend/index.html`
- 仲裁 API：`app/api/arbitration.py`
- 案件分析：`app/services/arbitration_analyzer.py`
- 文书生成：`app/services/arbitration_document_generator.py`
- 红蓝对抗：`app/agents/red_blue_lawyer.py`
- Agent 协调：`app/agents/coordinator.py`
- LLM 客户端：`app/services/llm_client.py`
- 重庆计算器：`app/services/chongqing_calculator.py`
- 工作流/证据/时效：`app/services/legal_workflow.py`
- 本地参考：`app/services/chongqing_precedent.py`
- 测试入口：`tests/test_local_arbitration.py`、`tests/test_labor_arbitration_cases.py`
- 案例矩阵报告脚本：`scripts/run_case_matrix.py`
- LangSmith 监测说明：`docs/status/LANGSMITH_MONITORING.md`
- Farui 风格后端映射：`docs/status/FARUI_BACKEND_MAPPING.md`
- 工作台 API：`app/api/workspace.py`
- 工作台助手：`app/services/legal_workspace_assistant.py`

## 已完成的重要改动

- 新增协作者状态文件夹：`docs/status/PROJECT_BRIEF.md`，集中说明项目定位、进度、接口、技术要求、分工和协作规则。
- 前端已重做为“接待式单案件界面”，不再沿袭旧的工作台 / SaaS 导航结构。
- 主界面改为“说案情 -> 看结论 -> 整理材料 -> 推进进度”的单案流程，文书、重庆参考、历史记录和本地身份都改为次级能力。
- 前端已隐藏 API 地址配置入口，默认同源请求，同时兼容旧的 `localStorage.lerap_api_base` 和 `window.LERAP_API_BASE` 注入。
- 前端已去掉英文工作台文案、伪登录表达和内部流水线直出，改为普通劳动者可理解的中文表达。
- 修复前端自然语言录入后“结果页把握说明为空”的问题。
- 优化前端自然语言抽取：避免把“重庆渝北一家公司”误识别成工作地或公司名称。
- 已加入庭前调解申请书生成。
- 已加入文书校验接口 `/arbitration/validate-document`。
- 已加入 20 个劳动仲裁典型案例测试。
- 已加入 10 类身份、20 个案例的后端稳定性报告脚本，输出 `output/case_matrix_latest.md/json`。
- 已接入可选 LangSmith 追踪封装和状态接口 `GET /arbitration/observability/langsmith`。
- `/arbitration/workup` 已增加 `pipeline_status` 阶段状态，包含阶段名、状态、耗时、摘要和警告，便于后端与 LangSmith 监测。
- 红蓝对抗结果已增加统一 `agent_result` 摘要，包含 agent_id、agent_name、status、summary、confidence、warnings。
- 修复未休年假工资纠纷被误识别为普通拖欠工资的问题。
- DeepSeek 模型接入配置已完成，用户已填写 API。
- 之前误做的“项目内部 LLM token 瘦身”已撤回，项目调用逻辑保持原状。
- 已参考 Farui 的法律咨询、文件审查、知识检索、技能工作台思路，新增后端 `/workspace/*` 能力：技能目录、案件文件、项目知识、知识检索、统一咨询、咨询历史。
- 新增 `LegalWorkspaceAssistant`，把法律咨询、文件审查、多维检索、庭审题纲、仲裁准备统一成固定技能，前端不需要直接拼 prompt。
- 工作台咨询已接入案件上下文、项目文件、项目知识、重庆本地检索、阶段状态和历史落库。
- 工作台输入已加长度限制，未知 `skill_id` 会稳定兜底为 `legal_consult` 并在 `pipeline_status` 中标记 warning，避免脏参数破坏调用链。

## 最近验证

- 2026-05-10：新版前端桌面与移动端联调通过，产出截图 `output/playwright/redesign-desktop.png`、`output/playwright/redesign-mobile.png`。
- 2026-05-10：Playwright 实测 `说案情 -> /arbitration/workup -> 看结论` 主流程通过，本地资料和历史快照正常出现。
- 2026-05-10：`.\.venv\Scripts\python.exe -m unittest discover -s tests -v` 通过，10 个测试 OK，新增首页重设计断言。
- 2026-05-10：`.\.venv\Scripts\python.exe -m compileall app tests` 通过。
- 2026-05-10：新增状态文档，本次未改业务代码，未运行测试。
- 2026-05-10：`.\.venv\Scripts\python.exe scripts\run_case_matrix.py` 通过，20/20 案例 PASS，报告已写入 `output/case_matrix_latest.md`。
- 2026-05-10：`.\.venv\Scripts\python.exe scripts\run_case_matrix.py` 通过，20/20 案例 PASS，验证 `pipeline_status` 和 `agent_result` 未破坏现有接口。
- 2026-05-10：`GET /arbitration/observability/langsmith` 返回 200，默认未启用追踪、不暴露密钥。
- 2026-05-10：`.\.venv\Scripts\python.exe -m unittest discover -s tests -v` 通过，10 个测试 OK。
- 2026-05-10：`.\.venv\Scripts\python.exe -m unittest discover -s tests -v` 通过，10 个测试 OK，新增流水线/Agent 契约断言。
- 2026-05-10：`.\.venv\Scripts\python.exe -m compileall app scripts tests` 通过。
- 2026-05-10：前端文案检查通过，未再出现 `API 地址`、`http://localhost`、`说清楚事实`、`看懂结果`、`拿到材料`、`红蓝对抗` 等前台暴露文本。
- 2026-05-11：`python -m compileall app scripts tests` 通过。
- 2026-05-11：`python -m unittest discover -s tests -v` 通过，11 个测试 OK，覆盖 Farui 风格工作台资源、咨询、技能兜底。
- 2026-05-11：`python scripts/run_case_matrix.py` 通过，20/20 案例 PASS，报告已写入 `output/case_matrix_latest.md/json`。
- `.\.venv\Scripts\python.exe -m compileall app tests` 通过。
- `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` 通过，8 个测试 OK。
- 测试中出现第三方 telemetry warning，不影响运行。

## Codex 工作约定

- 每次新任务先读本文件和 `docs/status/PROJECT_BRIEF.md`，不要默认全文阅读项目。
- 只读取与当前任务直接相关的文件。
- 优先使用精准搜索和局部文件片段，避免整项目扫描。
- 修改前先说明将改哪些文件。
- 每次完成实质改动后更新本文件的“已完成的重要改动”和“最近验证”。
- 文件数量尽量少，避免为小功能拆出过多新文件。
- 回复保持精简，重点说明改动、验证结果和风险。
