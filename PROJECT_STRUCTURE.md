# 重庆劳动法专家系统项目结构说明

## 项目概述
本项目是一个基于多Agent架构的重庆劳动法智能咨询系统，提供劳动仲裁辅助、文书生成、案件分析等功能。

## 项目目录结构

```
L-ERAP-PRO/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── webhooks.py
│   │   └── arbitration.py          # 仲裁相关API
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                 # Agent基类
│   │   ├── communication.py        # Agent通信机制
│   │   ├── chongqing_labor_law.py  # 重庆劳动法专家Agent
│   │   ├── classifier.py           # 案件分类器Agent
│   │   ├── coordinator.py          # 协调器Agent
│   │   ├── civil_law.py            # 民法专家Agent
│   │   ├── criminal_law.py         # 刑法专家Agent
│   │   └── red_blue_lawyer.py      # 红蓝对抗律师Agent
│   ├── config/
│   │   ├── __init__.py
│   │   ├── api_config.py           # API配置
│   │   ├── api_switch_config.py    # API切换配置
│   │   ├── llm_config.py           # LLM配置
│   │   └── settings.py             # 系统配置
│   ├── core/
│   │   ├── __init__.py
│   │   ├── graph.py                # LangGraph工作流
│   │   ├── nodes.py                # 工作流节点
│   │   └── state.py                # 状态定义
│   ├── knowledge/
│   │   ├── __init__.py
│   │   └── chongqing_labor.py      # 重庆劳动法知识库
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_factory.py          # API工厂
│   │   ├── arbitration_advisor.py  # 仲裁策略建议
│   │   ├── arbitration_analyzer.py # 仲裁分析服务
│   │   ├── arbitration_document_generator.py # 仲裁文书生成
│   │   ├── chongqing_calculator.py # 重庆劳动法计算引擎
│   │   ├── llm_client.py           # LLM客户端
│   │   └── rag_retriever.py        # RAG检索服务
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py               # 日志工具
│   └── data/
│       └── example_cases/
│           └── chongqing_sample_cases.json # 示例案例
├── scripts/
│   └── import_external_data.py # 外部数据导入脚本
├── docs/
│   └── 重庆劳动法专家系统开发项目文档手册.md # 项目文档
├── plans/
│   ├── L-ERAP-PRO-项目审查报告.md
│   ├── L-ERAP-PRO-魔塔API集成方案.md
│   ├── L-ERAP-PRO-多Agent律师智能体架构设计.md
│   ├── arbitration_api_design.md
│   ├── arbitration_assistant_design.md
│   ├── arbitration_components_design.md
│   ├── integration_plan.md
│   ├── opponent_review_process_design.md
│   ├── red_blue_lawyer_agent_design.md
│   ├── success_rate_improvement_logic.md
│   ├── test_plan.md
│   └── vulnerability_detection_mechanism.md
├── requirements.txt                # 依赖包列表
├── Dockerfile                      # 容器化配置
├── README.md                       # 项目说明
├── push.txt                        # 部署说明
└── test_*.py                       # 测试脚本
```

## 核心功能模块

### 1. 多Agent架构
- **协调器Agent (CoordinatorAgent)**: 协调各Agent工作
- **案件分类器Agent (CaseClassifierAgent)**: 案件分类和识别
- **重庆劳动法专家Agent (ChongqingLaborLawAgent)**: 专业法律分析
- **红蓝对抗律师Agent (RedBlueLawyerAgent)**: 对抗审查机制
- **民事法律专家Agent (CivilLawAgent)**: 民事法律咨询
- **刑事法律专家Agent (CriminalLawAgent)**: 刑事法律咨询

### 2. 核心服务模块
- **仲裁分析服务 (ArbitrationAnalyzer)**: 案件综合分析
- **仲裁文书生成器 (ArbitrationDocumentGenerator)**: 自动生成仲裁文书
- **重庆劳动法计算引擎 (ChongqingLaborCalculator)**: 赔偿计算
- **仲裁策略建议 (ChongqingArbitrationAdvisor)**: 仲裁策略推荐
- **RAG检索服务 (RAGRetriever)**: 法律条文和案例检索

### 3. API接口
- `/arbitration/analyze`: 案件分析接口
- `/arbitration/generate-document`: 文书生成接口
- `/arbitration/estimate-cost`: 成本估算接口
- `/arbitration/predict-success-rate`: 成功率预测接口
- `/arbitration/cases`: 案例查询接口

### 4. 特色功能
- **红蓝对抗机制**: 通过双重视角审视案件，提高成功率
- **API工厂模式**: 支持本地API和外部API（如魔塔社区API）切换
- **本地化特色**: 专为重庆地区劳动法设计
- **智能交互**: 自动识别用户意图并引导信息补全
- **法律条款溯源**: 每条法律建议都有明确出处
- **成本控制**: 通过分层模型和缓存降低使用成本

## 已实现的功能

### 1. 基础架构
- 多Agent协作架构
- LangGraph工作流引擎
- RESTful API接口设计
- 安全认证机制
- 日志记录系统

### 2. 仲裁辅助功能
- 案件综合分析（风险评估、成本估算、成功率预测）
- 仲裁文书生成（申请书、答辩书、证据清单、代理词）
- 成本估算系统
- 成功率预测模型
- 红蓝对抗审查机制

### 3. 重庆本地化特色
- 重庆劳动法计算引擎
- 重庆地区法律条文库
- 重庆劳动仲裁案例数据库
- 本地化法律条款溯源

### 4. 性能优化
- 缓存机制
- 异步处理
- 成本控制
- 高并发支持

## 依赖包列表

```txt
fastapi
uvicorn[standard]
langgraph>=0.0.30
langchain-openai
langchain-core
python-dotenv==1.0.0
loguru==0.7.2
tenacity==8.2.3
chromadb==0.5.0
sentence-transformers==2.2.2
requests==2.31.0
openai==1.54.0
```

## 开发说明

### 启动项目
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:create_app --host 0.0.0.0 --port 8000 --reload
```

### API配置
系统支持API工厂模式，可通过.env文件配置：
```
OPENAI_API_KEY=your_openai_api_key_here
MAGIC_TOWER_API_KEY=your_magic_tower_api_key_here
```

### API使用示例
```bash
# 运行API使用示例
python api_usage_example.py
```

### 测试功能
```bash
# 运行仲裁功能测试
python test_arbitration_functionality.py

# 运行对抗机制测试
python test_opposition_mechanism.py

# 运行使用示例
python arbitration_usage_example.py
python opposition_usage_example.py
```

## 项目特点

1. **专业性强**: 专门针对重庆地区劳动法设计
2. **功能完整**: 覆盖仲裁全流程
3. **智能高效**: 多Agent协同，智能分析
4. **易于扩展**: 模块化设计，便于功能扩展
5. **安全可靠**: 完善的安全机制和质量保障
6. **性能优良**: 高并发支持和成本控制