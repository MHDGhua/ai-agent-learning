# L-ERAP-PRO 项目状态总览

最后更新：2026-05-11

## 阅读目的

这是给后续工作人员的入口文件。新成员应先读本文件，再按任务读取少量相关代码，避免每次全文阅读项目。

## 项目一句话定位

L-ERAP-PRO 是一个面向普通劳动者的重庆劳动仲裁助手。用户用自然语言描述劳动争议，后端负责整理案情、判断关键缺口、评估风险、默认执行红蓝对抗、生成仲裁材料，并结合重庆本地规则和参考资料辅助用户准备仲裁。

## 产品边界

- 目标用户：需要劳动仲裁帮助的普通劳动者。
- 非目标用户：专业律师后台、法院/仲裁委内部系统、全国通用法律百科。
- 重点场景：欠薪、违法解除、加班费、工伤待遇、社保/劳动关系确认、新就业形态争议。
- 核心体验：用户只需要把事实说清楚，系统在后台完成计算、检索、分析和材料生成。
- 前端原则：普通用户导向，低术语、低密度、少暴露内部机制。
- 后端原则：接口稳定、字段清晰、规则可测试、LLM 接入可替换。

## 当前角色分工

- 当前 Codex 角色：后端工程师。
- 后端负责范围：API 契约、业务逻辑、Agent 流程、DeepSeek/LLM 接入、RAG/本地知识、文书生成、测试。
- 前端默认不归当前 Codex 直接负责。除非用户明确要求，不主动修改前端界面和样式。
- 若用户明确要求前端改版，优先遵守“普通劳动者导向、低术语、少暴露内部机制”的产品边界。
- 如后端变更影响前端，只说明接口变化并保持向后兼容。

## 当前核心模块

- `app/api/arbitration.py`：劳动仲裁主 API，聚合分析、文书、校验、参考资料。
- `app/services/arbitration_analyzer.py`：案件分析入口，组合规则分析、成本估算、成功率预测、本地参考。
- `app/services/legal_workflow.py`：管辖、时效、诉求、证据清单等工作流规则。
- `app/services/arbitration_document_generator.py`：仲裁申请书、证据清单、庭前调解申请书生成。
- `app/agents/red_blue_lawyer.py`：红蓝对抗审查，模拟劳动者和企业两侧观点。
- `app/agents/coordinator.py`：Agent 协调与最终意见整合。
- `app/services/llm_client.py`：LLM 统一客户端，支持 local、OpenAI、魔塔、DeepSeek 等提供商。
- `app/services/chongqing_calculator.py`：重庆劳动争议金额计算能力。
- `app/services/chongqing_precedent.py`：重庆本地参考资料组织。
- `app/services/rag_retriever.py`：RAG 检索入口。
- `app/api/workspace.py`：Farui 风格后端工作台入口，提供技能、文件、知识、咨询和历史。
- `app/services/legal_workspace_assistant.py`：工作台统一助手，负责技能路由、文件审查、知识召回和咨询输出。
- `tests/test_local_arbitration.py`：本地 API 与核心功能合同测试。
- `tests/test_labor_arbitration_cases.py`：20 个典型劳动仲裁案例测试。

## 主要 API 契约

- `POST /arbitration/workup`：产品化综合研判，一次返回分析、补证、成本、成功率、本地参考、建议文书和服务建议。
- `POST /arbitration/analyze`：案件分析，返回风险、概率、管辖、时效、证据、红蓝对抗等结构化结果。
- `POST /arbitration/generate-document`：按文书类型生成材料，支持仲裁申请书、证据清单、庭前调解申请书。
- `POST /arbitration/validate-document`：校验文书内容与案件信息是否一致。
- `POST /arbitration/estimate-cost`：估算仲裁准备成本。劳动争议仲裁本身不收费。
- `POST /arbitration/predict-success-rate`：基于证据质量、数量和背景做规则化成功率预测。
- `POST /arbitration/calculate-claim`：内部金额快算能力，可算经济补偿/违法解除、加班费、工伤一次性伤残补助金。
- `POST /arbitration/intake-checklist`：返回还需要补充的问题、证据清单、管辖和时效信息。
- `GET /arbitration/local-references`：返回重庆本地法规、案例或办事参考摘要。
- `GET /workspace/skills`：返回 Farui 风格的固定技能目录。
- `POST /workspace/cases/{case_id}/files`：把文本文件加入案件工作台。
- `GET /workspace/cases/{case_id}/files`：查看案件文件。
- `POST /workspace/cases/{case_id}/knowledge`：保存项目内知识条目。
- `GET /workspace/cases/{case_id}/knowledge`：查看项目内知识。
- `GET /workspace/knowledge/search`：检索重庆本地参考和知识召回结果。
- `POST /workspace/cases/{case_id}/consult`：统一咨询入口，按技能、文件、知识和案件上下文输出结果。
- `GET /workspace/cases/{case_id}/messages`：查看案件咨询历史。

## 重要技术要求

- Python 后端，FastAPI 提供 HTTP API。
- Pydantic 用于请求/响应模型。
- LangChain / LangGraph 用于部分 LLM 和工作流能力。
- DeepSeek 官方模型已接入配置，API Key 由用户在 `.env` 自行填写。
- `LLM_PROVIDER` 控制模型提供商，`local` 模式用于本地测试和兜底。
- RAG 使用本地检索能力和重庆本地资料，不应无节制引入全国泛化信息。
- 文书生成必须可审计、可校验，不应直接承诺法律结果。
- 测试以本地规则可跑通为底线，不能依赖真实外部 LLM 才能通过。
- 工作台咨询不直接暴露 prompt 拼接给前端，技能选择由后端兜底，未知值会回落到 `legal_consult`。
- 文件与知识输入要加长度限制，避免单次咨询把上下文和存储撑爆。

## 当前已完成进度

- 基础 FastAPI API 已具备。
- 仲裁综合研判 `/arbitration/workup` 已具备。
- 红蓝对抗默认开启。
- 重庆本地参考能力已接入。
- 金额快算已作为后端内部能力存在，不作为前台独立重点展示。
- 仲裁申请书、证据清单、庭前调解申请书已支持生成。
- 文书一致性校验接口已支持。
- DeepSeek 官方模型配置已接入。
- 20 个劳动仲裁典型案例测试已编写。
- Farui 风格后端工作台已接入，包含技能目录、案件文件、项目知识、咨询历史和统一咨询入口。
- 前端已重做为接待式单案件布局：首页围绕自然语言录入和关键结论，不再沿袭旧工作台导航和英文模块命名。
- 前端已隐藏 API 地址配置入口，保留同源请求与历史兼容注入，不再向普通用户暴露部署配置。

## 当前验证状态

- 最近一次已知验证：`.\.venv\Scripts\python.exe -m compileall app tests` 通过。
- 最近一次已知验证：`.\.venv\Scripts\python.exe -m unittest discover -s tests -v` 通过，10 个测试 OK。
- 最近一次已知验证：Playwright 联调桌面端与移动端新版前端通过，截图输出 `output/playwright/redesign-desktop.png`、`output/playwright/redesign-mobile.png`。
- 最近一次已知验证：`python -m compileall app scripts tests` 通过。
- 最近一次已知验证：`python -m unittest discover -s tests -v` 通过，11 个测试 OK。
- 最近一次已知验证：`python scripts/run_case_matrix.py` 通过，20/20 案例 PASS。
- 测试中可能出现第三方 telemetry warning，不影响功能运行。

## 后续开发优先级

- 稳定后端接口契约，避免破坏现有前端调用。
- 强化 `/arbitration/workup` 的字段质量，保证普通用户需要的结果能由前端直接展示。
- 提高文书生成和校验的准确性，尤其是金额、当事人、证据、法条一致性。
- 完善重庆本地知识库和可追溯来源。
- 增加更多后端测试，覆盖长案情、缺失字段、不同争议类型、DeepSeek 配置兜底。
- 对 LLM 调用做可配置策略，但未经用户确认不要改变当前项目默认推理路径。
- 使用 `scripts/run_case_matrix.py` 可生成 10 类身份、20 个劳动案例的后端稳定性报告，结果输出到 `output/case_matrix_latest.md` 和 `output/case_matrix_latest.json`。
- LangSmith 已作为可选监测接入，配置说明见 `docs/status/LANGSMITH_MONITORING.md`。

## 协作规则

- 新任务先读 `PROJECT_STATE.md` 和本文件。
- 不要默认全文阅读项目。
- 优先精准读取相关文件片段。
- 文件数量尽量少，避免把小功能拆散。
- 当前 Codex 不主动改前端。
- 修改后端接口时，必须说明是否影响前端调用字段。
- 每次完成实质改动后更新 `PROJECT_STATE.md`，必要时更新本文件。

## 风险与注意事项

- 法律类产品不能承诺胜诉结果，所有输出都应标明仅供材料准备和风险提示。
- 重庆本地规则和工资/社平/工伤标准可能随时间变化，涉及实时标准时应核验来源。
- DeepSeek API Key 不应写入代码或文档示例，只从 `.env` 读取。
- 红蓝对抗是辅助审查，不等同于律师正式意见。
- 金额计算结果必须可解释、可复核，不能只给总数。
