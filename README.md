# 重庆劳动法专家系统 (解耦版本)

## 项目概述

这是一个基于多Agent架构的重庆劳动法智能咨询系统，提供劳动仲裁辅助、文书生成、案件分析等功能。本项目已进行解耦重构，将数据处理、文档处理和数据导入功能分离到独立模块中，提高了系统的可维护性和可扩展性。

## 项目结构

```
L-ERAP-PRO/
├── app/
│   ├── api/                    # API接口模块
│   ├── agents/                 # Agent智能体模块
│   ├── config/                 # 配置文件模块
│   ├── services/               # 服务模块
│   │   ├── data_processing/    # 数据处理模块（已解耦）
│   │   │   ├── __init__.py
│   │   │   ├── data_cleaner.py # 数据清洗功能
│   │   │   └── document_processor.py # 文档处理功能
│   │   ├── data_import/        # 数据导入模块（已解耦）
│   │   │   ├── __init__.py
│   │   │   └── data_importer.py # 数据导入和存储功能
│   │   ├── __init__.py
│   │   └── ...                 # 其他服务模块
│   ├── utils/                  # 工具模块
│   └── ...                     # 其他模块
├── scripts/                    # 脚本文件
│   ├── process_laborlaw_dataset.py # 数据处理脚本
│   └── import_external_data.py   # 数据导入脚本
├── data/                       # 数据目录
│   ├── processed_laborlaw/     # 处理后的劳动法数据
│   └── chroma_db/              # Chroma知识库数据
└── requirements.txt            # 依赖包列表
```

## 解耦模块说明

### 1. 数据处理模块 (`app/services/data_processing/`)

此模块包含所有数据处理相关的功能，包括：
- **DataCleaner**: 数据清洗功能，用于清理和标准化文本数据
- **DocumentProcessor**: 文档处理功能，支持多种文档格式的处理

### 2. 数据导入模块 (`app/services/data_import/`)

此模块负责数据的导入、存储和检索功能：
- **DataImporter**: 数据导入器，支持JSON、CSV等多种格式的数据导入
- 使用ChromaDB作为知识库存储后端
- 支持TF-IDF嵌入向量生成

## 核心功能

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

### 4. API工厂配置
本系统支持API工厂模式，可灵活切换不同API服务：
- **本地API**: 默认使用本地服务
- **魔塔社区API**: 支持连接魔塔社区API服务

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

### 打开前端界面
启动服务后，直接访问根路径即可打开新版前端：

- `http://127.0.0.1:8000/`
- 前端入口文件位于 `frontend/index.html`
- 当前界面已改为面向普通劳动者的接待式单案件布局，以自然语言录入为核心
- 二级能力包括：文书中心、重庆参考、历史记录和本地身份信息

### 本地模式说明
默认使用本地兜底模式，不依赖外部大模型即可完成案件分析、文书生成和基础测试。
如需启用 Chroma 向量检索，可额外设置：
```bash
ENABLE_CHROMA_RETRIEVAL=true
```

### 生产部署
多容器部署说明见 [docs/deployment.md](docs/deployment.md)。

### 处理数据集
```bash
python scripts/process_laborlaw_dataset.py
```

### 导入外部数据
```bash
python scripts/import_external_data.py
```

## 技术栈

- **后端框架**: FastAPI
- **AI模型**: OpenAI API
- **知识库**: ChromaDB
- **文档处理**: python-docx, PyPDF2, pandas
- **嵌入模型**: TF-IDF (本地实现)
- **部署**: Docker

## 项目特点

1. **专业性强**: 专门针对重庆地区劳动法设计
2. **功能完整**: 覆盖仲裁全流程
3. **智能高效**: 多Agent协同，智能分析
4. **易于扩展**: 模块化设计，便于功能扩展
5. **安全可靠**: 完善的安全机制和质量保障
6. **性能优良**: 高并发支持和成本控制

## 开发说明

### 目录结构说明
- `app/`: 主应用代码
- `scripts/`: 数据处理和导入脚本
- `data/`: 数据存储目录
- `docs/`: 项目文档
- `tests/`: 测试代码

### 配置说明
配置文件位于 `app/config/` 目录下，包括：
- `settings.py`: 系统基础配置
- `combined_config.py`: 合并的LLM和API配置

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License
