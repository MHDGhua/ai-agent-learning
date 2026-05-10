# PROJECT_STATE

最后更新：2026-05-10
当前验收版本：v1.3.0

## 项目定位

L-ERAP-PRO 是面向普通劳动者的重庆劳动仲裁助手，不是专业律师工作台。核心目标是让用户用自然语言描述纠纷，系统完成案情整理、风险提示、红蓝对抗、文书生成和重庆本地参考。

## 当前产品方向

- 官网采用同风格原创浅色法律科技首页，工作区使用 `/assistant` 路由承载案件办理。
- 主界面以案件输入、研判摘要和文书草稿为核心，只展示最关键结论。
- 二级功能放入侧边栏：历史、助手、文书、重庆参考。
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

## 已完成的重要改动

- 前端已重设计为“官网入口 + 案件助手工作区”双层结构：首页是法睿风格浅色官网、左侧导航和中心输入区，`/assistant` 进入浅色助手办理区。
- 前台已清理内部工程表达，不再向用户直出 API 基址、流水线状态、耗时毫秒或服务端实现细节；后端 `pipeline_status` 仍保留为接口契约，前端转译为“办理进度”。
- 前端已把后端 `workflow_stage`、`pipeline_status` 和阶段状态翻译成用户可读文案，避免把内部阶段名直接露给页面。
- 新增前端源码断言，检查官网能力库文案存在且内部运行细节不出现在可见组件中。
- 新增 `/assistant` 前端入口路由，首页和工作区都可直接刷新访问。
- FastAPI 根路径 `/` 已对齐 Vite 构建产物加载：构建后返回 `frontend/dist/index.html`，同域 `/assets/*` 提供静态资源。
- 新增静默登录态接口 `GET /auth/session`，前端首屏不再用 `/auth/me` 触发未登录 401；`/auth/me` 继续保留为严格认证接口。
- 认证与工作区逻辑已新增服务层：`app/services/auth_service.py`、`app/services/workspace_service.py`，路由不再直接承担全部持久化调用细节。
- 已新增账户资料更新接口 `PUT /auth/profile`，支持修改姓名和身份标签。
- 已新增旧版浏览器本地记录导入接口 `POST /workspace/import-legacy`，可把旧 `localStorage` 历史案件和活动记录迁入服务端。
- 前端主页面已拆分为组件与 composable：`frontend/src/components/*` 与 `frontend/src/composables/useWorkspaceApp.js`，不再把所有状态和视图堆在单个 `App.vue`。
- v1.3.0 已完成：前端路由页面拆分、真实账户与服务端持久化、认证增强、全局异常与请求日志、服务层类型补强、LLM 重试、RAG 降级、官方级首页与使用界面改造。
- 已从 Git 移除 `data/chroma_db/` Chroma 运行态二进制索引，并加入 `.gitignore`；知识库可通过导入脚本或运行时按需重新生成。
- 仲裁接口请求/响应模型已从 `app/api/arbitration.py` 拆分到 `app/schemas/arbitration.py`，开始收敛 API 层与 Schema 层职责。
- 真实账户已补充修改密码接口 `/auth/change-password`，新密码要求至少 8 位且同时包含字母和数字，修改后旧会话全部失效并重新签发当前会话。
- 前端已接入文书校验结果展示，生成文书后会自动调用 `/arbitration/validate-document`，展示问题、警告和建议。
- 登录用户在案情分析和文书生成后会自动把当前案件快照保存到服务端，减少手动保存遗漏。
- 新增真实账户与服务端持久化基础能力：`/auth/register`、`/auth/login`、`/auth/logout`、`/auth/me`、`/workspace/cases`、`/workspace/activities` 已可用，使用 SQLite 保存用户、会话、案件快照和活动记录。
- 新增 `app/core/persistence.py` 轻量持久化层，默认数据库切到 `data/runtime/lerap_app.db`，密码采用 PBKDF2 哈希，登录会话采用 HttpOnly Cookie。
- 前端已从单文件静态页切换到 Vue 3 + Vite 工程结构，入口改为 `frontend/src/App.vue`，支持登录、案情分析、文书生成和服务端保存案件。
- 生产部署已改为 Docker 多阶段构建前端产物，由 FastAPI 统一提供前端静态资源，Caddy 只保留同域 HTTPS 反向代理职责。
- `tests/test_api_integration.py` 已改为可被 `unittest discover` 发现的真实回归测试，不再空跑。
- 后端统一错误返回已收敛为通用提示，避免把内部异常原文直接暴露给客户端。
- 新增本轮验收文档：`docs/初步验收报告与操作手册.md`。
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

## 最近验证

- 2026-05-10：`npm run build` 通过；`python -m pytest tests` 通过，51 passed；Playwright 视觉检查 `/` 与 `/assistant` 通过，截图保存到 `.playwright-cli/lerap-official-home.png` 与 `.playwright-cli/lerap-assistant-workspace.png`。
- 2026-05-10：清理仓库内 `data/chroma_db/` 运行态二进制索引前，确认默认 `ENABLE_CHROMA_RETRIEVAL=false` 且 RAG 有 JSON/processed 文件降级路径。
- 2026-05-10：`cd frontend && npm run build` 通过，产物已刷新；Playwright 实测 `/`、`/assistant` 和“整理案情并评估”主流程通过，截图已保存为 `output/playwright/farui-home-desktop.png` 与 `output/playwright/farui-workspace-desktop.png`。
- 2026-05-10：`.\.venv\Scripts\python.exe -m unittest discover -s tests -v` 通过，50 个测试 OK。
- 2026-05-10：`.\.venv\Scripts\python.exe -m compileall app tests` 通过。
- 2026-05-10：`git diff --check` 通过。
- 2026-05-10：`cd frontend && npm run build` 通过，已刷新 `frontend/dist`，根路径加载的构建包使用 `/auth/session` 做静默登录态探测。
- 2026-05-10：`.\.venv\Scripts\python.exe -m compileall app tests` 通过。
- 2026-05-10：`.\.venv\Scripts\python.exe -m unittest tests.test_local_arbitration -v` 通过，11 个测试 OK，覆盖 FastAPI 根路径静态资源、静默 session、严格 `/auth/me` 与工作区持久化。
- 2026-05-10：`cd frontend && npm run build` 通过，官网入口与助手工作区重设计可正常构建。
- 2026-05-10：`python -m unittest discover -s tests -v` 通过，15 个测试 OK，`tests/test_api_integration.py` 已纳入自动发现。
- 2026-05-10：`python -m compileall app tests` 通过。
- 2026-05-10：`python scripts/run_case_matrix.py` 通过，20/20 案例 PASS。
- 2026-05-10：`cd frontend && npm run build` 通过，前端重新构建成功。
- 2026-05-10：`python -m unittest discover -s tests -v` 通过，12 个测试 OK，`tests/test_api_integration.py` 已纳入自动发现。
- 2026-05-10：`cd frontend && npm run build` 通过，前端组件化拆分后仍可正常构建。
- 2026-05-10：`.\.venv\Scripts\python.exe -m compileall app tests` 通过，新增服务层与迁移接口未破坏编译。
- 2026-05-10：`.\.venv\Scripts\python.exe -m unittest discover -s tests -v` 通过，11 个测试 OK，新增修改密码链路回归。
- 2026-05-10：`cd frontend && npm run build` 通过，前端已包含自动保存与文书校验展示改动。
- 2026-05-10：`.\.venv\Scripts\python.exe -m compileall app tests` 通过，新增 `app/schemas/arbitration.py` 与认证安全改动未破坏编译。
- 2026-05-10：`cd frontend && npm install && npm run build` 通过，Vite 前端成功产出 `frontend/dist/`。
- 2026-05-10：`.\.venv\Scripts\python.exe -m unittest discover -s tests -v` 通过，11 个测试 OK，新增真实账户与服务端保存链路测试。
- 2026-05-10：`.\.venv\Scripts\python.exe -m compileall app tests` 通过。
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
