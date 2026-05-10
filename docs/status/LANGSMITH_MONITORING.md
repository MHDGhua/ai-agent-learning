# LangSmith 监测接入说明

最后更新：2026-05-10

## 接入目的

用于可视化观察每次劳动仲裁请求的执行链路：入口 API、案件分析、红蓝对抗、文书生成、校验、LLM 调用耗时和错误。

## 当前接入状态

- 已新增可选追踪封装：`app/services/observability.py`
- 已给核心仲裁 API 增加 LangSmith trace 名称：
  - `arbitration.workup`
  - `arbitration.analyze`
  - `arbitration.analyze_local`
  - `arbitration.generate_document`
  - `arbitration.validate_document`
- 已新增状态接口：`GET /arbitration/observability/langsmith`
- 默认不启用追踪，避免把用户案情和个人信息发送到外部平台。

## 启用方式

在 `.env` 中设置：

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=填写你的 LangSmith Key
LANGSMITH_PROJECT=L-ERAP-PRO
```

可选：

```env
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_CALLBACKS_BACKGROUND=false
```

说明：`LANGCHAIN_CALLBACKS_BACKGROUND=false` 适合测试或短生命周期任务，能减少进程退出前 trace 未提交的情况；生产常驻服务可不设置。

## 如何查看

1. 启动后端服务。
2. 访问 `GET /arbitration/observability/langsmith`，确认：
   - `tracing_enabled=true`
   - `api_key_configured=true`
   - `dependency_available=true`
3. 调用 `/arbitration/workup`。
4. 打开 LangSmith 项目 `L-ERAP-PRO`，查看 trace。

## 隐私注意

LangSmith 追踪会记录输入、输出和模型调用过程。劳动仲裁案情可能包含姓名、电话、公司名称、工资、聊天记录等敏感信息。生产环境启用前应先决定脱敏策略和数据保留策略。

## 官方依据

- LangSmith tracing quickstart：`https://docs.langchain.com/langsmith/observability-quickstart`
- LangChain tracing integration：`https://docs.langchain.com/langsmith/trace-with-langchain`

