# Farui 风格后端改造映射

最后更新：2026-05-11

## 参考对象

- 访问页面：`https://farui.aliyun.com/farui/v1`
- 观察到的公开功能入口：法律咨询、专业文件审查、多维度法律检索、项目/历史、文件、知识、技能。
- 官方能力参考：
  - [通义法睿产品介绍](https://help.aliyun.com/zh/model-studio/tongyi-farui/)
  - [法律咨询接口](https://help.aliyun.com/zh/model-studio/api-farui-2024-06-28-runlegaladviceconsultation)
  - [案例全文检索接口](https://help.aliyun.com/zh/model-studio/api-farui-2024-06-28-runsearchcasefulltext)
  - [合同智能审查接口](https://help.aliyun.com/zh/model-studio/api-farui-2024-06-28-runcontractrulegeneration)

## 后端映射原则

本项目不照搬 Farui 的通用法律平台形态，而是把它的“法律工作台能力”映射到重庆劳动仲裁场景：

- 项目/历史：沿用 `workspace` 案件工作台。
- 法律咨询：接入案件上下文和劳动仲裁规则。
- 文件审查：支持把起诉状、答辩状、代理词、合同草稿等文本保存到案件并审查。
- 知识检索：复用重庆本地资料和 RAG 检索。
- 技能：以固定技能目录驱动后端任务，不让前端直接拼 prompt。
- 历史记录：咨询结果落库，支持按案件查看。

## 新增后端能力

- `GET /workspace/skills`
  返回后端可运行的技能目录。

- `POST /workspace/cases/{case_id}/files`
  向案件项目添加文本文件。

- `GET /workspace/cases/{case_id}/files`
  查看案件项目文件。

- `POST /workspace/cases/{case_id}/knowledge`
  保存项目内知识条目。

- `GET /workspace/cases/{case_id}/knowledge`
  查看项目内知识条目。

- `GET /workspace/knowledge/search`
  检索本地法规、案例、重庆参考资料。

- `POST /workspace/cases/{case_id}/consult`
  Farui 风格统一咨询入口。支持 `skill_id`、`file_ids`、`knowledge_query`、`deep_think`、`online_search`。

- `GET /workspace/cases/{case_id}/messages`
  查看案件项目下的咨询历史。

## 接口约束

- 所有 `/workspace/*` 接口沿用当前登录态，不新增独立鉴权机制。
- `POST /workspace/cases/{case_id}/consult` 是统一入口，前端只传 `message`、可选 `skill_id`、`file_ids`、`knowledge_query`、`deep_think`、`online_search`。
- 未传 `skill_id` 时由后端根据问题和文件名推断技能。
- 传入未知 `skill_id` 时稳定回落到 `legal_consult`，并在 `pipeline_status` 的 `resolve_skill` 阶段标记 `warning`。
- 文件内容限制为 120000 字符，项目知识内容限制为 80000 字符，单次咨询问题限制为 6000 字符，单次关联文件最多 10 个。
- 当前文件能力先支持文本保存和审查，不做真实二进制上传；如后续需要 PDF/Word，应复用 `DocumentProcessor` 并单独设计 multipart 接口。

## 示例调用

```http
GET /workspace/skills
```

```json
{
  "items": [
    {
      "id": "legal_consult",
      "name": "法律咨询",
      "kind": "consult"
    }
  ]
}
```

```http
POST /workspace/cases/{case_id}/consult
```

```json
{
  "message": "阅读申请书草稿，整理庭审问答题纲。",
  "skill_id": "hearing_outline",
  "file_ids": [1],
  "knowledge_query": "重庆 工资 拖欠",
  "deep_think": true
}
```

响应重点字段：

- `skill_id` / `skill_name`：实际执行技能。
- `assistant_message`：面向普通用户的结果文本。
- `citations`：引用的文件、项目知识、本地参考。
- `next_actions`：下一步动作。
- `pipeline_status`：工作台执行状态，便于 LangSmith 或前端监测。
- `related_files` / `related_knowledge`：本次咨询关联资源。

## 技能目录

- `legal_consult`：法律咨询。
- `file_review`：文件审查。
- `knowledge_search`：法规/案例/本地参考检索。
- `hearing_outline`：庭审问答题纲。
- `arbitration_workup`：仲裁准备。

## 主要文件

- `app/api/workspace.py`
- `app/schemas/workspace.py`
- `app/core/persistence.py`
- `app/services/legal_workspace_assistant.py`
- `tests/test_local_arbitration.py`

## 验证

- `python -m compileall app scripts tests` 通过。
- `python -m unittest discover -s tests -v` 通过，11 个测试 OK。
- `python scripts/run_case_matrix.py` 通过，20/20 案例 PASS。
- 已加回归断言：未知技能回落到 `legal_consult` 并输出 `pipeline_status` warning。
