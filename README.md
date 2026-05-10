# 重庆劳动法专家系统

## 项目概述

这是一个面向普通劳动者的重庆劳动仲裁助手，后端基于 FastAPI 与多 Agent 规则/检索能力，前端采用 Vue 3 + Vite 工作台，支持真实账户、服务端案件保存、案情分析、文书生成和重庆本地参考。

## 项目结构

```
L-ERAP-PRO/
├── app/                        # FastAPI 后端、Agent、规则与持久化
├── frontend/                   # Vue 3 + Vite 前端
├── docs/                       # 项目与部署文档
├── scripts/                    # 数据处理与验证脚本
├── tests/                      # 后端合同与场景测试
└── data/                       # 知识库、运行态与输出数据
```

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

### 安装后端依赖
```bash
pip install -r requirements.txt
```

### 安装前端依赖
```bash
cd frontend
npm install
cd ..
```

### 启动后端
```bash
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

### 启动前端开发服务器
```bash
cd frontend
npm run dev
```

### 打开前端界面

- 开发模式：`http://127.0.0.1:5173/`
- 构建后或容器模式：`http://127.0.0.1:8000/`

- 前端源码入口位于 `frontend/src/App.vue`
- API 默认走同源，也可通过 `VITE_API_BASE_URL` 指向独立后端地址
- 登录成功后，案件快照、文书草稿和活动记录会保存到服务端 SQLite

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
- **前端框架**: Vue 3 + Vite
- **AI模型**: OpenAI API
- **知识库**: ChromaDB
- **文档处理**: python-docx, PyPDF2, pandas
- **嵌入模型**: TF-IDF (本地实现)
- **持久化**: SQLite（默认）
- **部署**: Docker + Caddy

## 项目特点

1. **专业性强**: 专门针对重庆地区劳动法设计
2. **功能完整**: 覆盖仲裁全流程
3. **智能高效**: 多Agent协同，智能分析
4. **易于扩展**: 模块化设计，便于功能扩展
5. **安全可靠**: 完善的安全机制和质量保障
6. **性能优良**: 高并发支持和成本控制

## 开发说明

### 目录结构说明
- `app/`: 主应用代码与 API
- `frontend/`: Vite 前端源码与构建配置
- `scripts/`: 数据处理和导入脚本
- `data/`: 数据和运行态目录
- `docs/`: 项目文档
- `tests/`: 测试代码

### 配置说明
配置文件位于 `app/config/` 目录下，包括：
- `settings.py`: 系统基础配置
- `combined_config.py`: 合并的LLM和API配置
- `DATABASE_URL`: 默认 `sqlite:///./data/runtime/lerap_app.db`
- `SESSION_COOKIE_SECURE`: 生产环境建议设为 `true`

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License
