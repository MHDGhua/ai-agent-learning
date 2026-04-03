# 🤖 AI Agent - 智能助手

这是一个基于 **ReAct 模式** 的 AI Agent 项目，支持调用真实天气 API、从私有知识库中检索文档（RAG），并提供命令行和 Web 界面两种交互方式。

---

## 📌 主要功能

- **智能对话**：基于 Azure OpenAI（GPT 模型）进行自然语言理解与生成  
- **天气查询**：调用和风天气 API，支持任意城市（自动获取 LocationID）  
- **知识库检索（RAG）**：支持上传 PDF、Word、PPT、TXT 等文档，自动索引并回答相关问题  
- **工程化能力**：自动重试、结构化日志、环境变量配置  
- **Web 界面**：基于 Streamlit，支持对话历史记录  

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 大模型 | Azure OpenAI (GPT-3.5/4) |
| 嵌入模型 | `BAAI/bge-small-zh-v1.5` (中文优化) |
| 向量数据库 | Chroma (本地持久化) |
| 文本切块 | LangChain `RecursiveCharacterTextSplitter` |
| 文档解析 | PyPDF, python-docx, python-pptx |
| Web 框架 | Streamlit |
| 日志 | Loguru |
| 重试 | Tenacity |
| 环境管理 | python-dotenv |

---

## 📂 项目结构
first_agent/
├── app.py # Streamlit Web 界面
├── react_agent.py # ReAct 主循环
├── azure_llm.py # Azure OpenAI 调用封装（带重试）
├── weather_tool.py # 和风天气 API 工具（支持任意城市）
├── rag_tool.py # RAG 检索工具（向量检索 + 重排序）
├── indexer.py # 文档索引脚本（支持多种格式）
├── document_loader.py # 文档加载器（PDF/Word/PPT/Markdown）
├── logger_config.py # 日志配置（控制台 + 文件）
├── test_retrieve.py # 检索功能测试脚本
├── check_db.py # 查看向量数据库内容
├── requirements.txt # 依赖列表
├── .env.example # 环境变量模板
└── knowledge/ # 待索引的文档文件夹（需自行创建）

---

## 🚀 快速开始

### 1. 克隆仓库
git clone https://github.com/MHDGhua/ai-agent-learning.git
cd ai-agent-learning/first_agent

### 2. 创建虚拟环境并激活
python -m venv venv
source venv/bin/activate        # Linux/macOS
.\venv\Scripts\activate         # Windows

### 3. 安装依赖
pip install -r requirements.txt

### 4. 配置环境变量
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_azure_key
AZURE_OPENAI_DEPLOYMENT=your_deployment_name

HEFENG_KEY=your_hefeng_key      # 和风天气 API Key

### 5. 索引文档（首次使用 RAG 时）
python indexer.py

### 6. 运行命令行 Agent
python react_agent.py

### 7. 运行 Web 界面
streamlit run app.py

### 🧠 核心模块说明
## react_agent.py
ReAct 主循环：

def react_agent(user_input: str, max_steps: int = 5) -> str:
    prompt = f"""...工具描述...用户问题...格式要求..."""
    for step in range(max_steps):
        llm_output = call_llm(prompt)
        if "Final Answer:" in llm_output:
            return llm_output.split("Final Answer:")[-1].strip()
        action, action_input = extract_action(llm_output)
        if action not in tools:
            return f"未知工具：{action}"
        observation = tools[action](action_input)
        prompt += f"\nObservation: {observation}\n"
    return "超过最大步数"

构建提示词（包含工具描述、格式要求）
调用 call_llm 获取 Thought、Action、Action Input
解析并执行对应工具
将观察结果追加到提示词，循环直至得到 Final Answer

## azure_llm.py —— Azure OpenAI 调用封装
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-12-01-preview"  # 支持 o4-mini 等模型
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "你是一个智能助手..."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=500
    )
    return response.choices[0].message.content

重试装饰器：网络抖动或限流时自动重试（指数退避），提高稳定性。
配置外置：所有敏感信息（终结点、密钥、部署名）均从 .env 读取。
API 版本适配：针对你使用的 o4-mini 模型，使用了 max_completion_tokens 而非 max_tokens，且不支持 temperature 参数。
统一接口：隐藏了复杂的 Azure 认证和 API 细节，上层只需传入 prompt。

## weather_tool.py

def get_location_id(city_name: str) -> str:
    geo_url = "https://pn5egmpvnu.re.qweatherapi.com/geo/v2/city/lookup"
    params = {"location": city_name, "key": HEFENG_KEY}
    resp = requests.get(geo_url, params=params)
    data = resp.json()
    if data.get("code") == "200":
        return data["location"][0]["id"]
    return None

def get_weather(city: str) -> str:
    loc_id = get_location_id(city)
    if not loc_id:
        return f"无法识别城市：{city}"
    weather_url = "https://pn5egmpvnu.re.qweatherapi.com/v7/weather/now"
    params = {"location": loc_id, "key": HEFENG_KEY}
    resp = requests.get(weather_url, params=params)
    data = resp.json()
    if data.get("code") == "200":
        now = data["now"]
        return f"{city} 当前天气：{now['text']}，温度 {now['temp']}℃"
    return f"天气查询失败：{data.get('code')}"

使用和风天气 GeoAPI 将城市名转换为 LocationID
调用实时天气接口获取天气数据
支持任意城市（中文、拼音）

## rag_tool.py
从 Chroma 向量库中检索与问题最相似的文档片段
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(
    name="my_knowledge",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name='BAAI/bge-small-zh-v1.5'
    )
)

def retrieve_documents(query: str, top_k: int = 2) -> str:
    results = collection.query(query_texts=[query], n_results=top_k)
    if results['documents'][0]:
        return "\n\n".join(results['documents'][0])
    return "未找到相关信息"

可选：使用 bge-reranker-small 进行重排序（需额外安装 FlagEmbedding）

返回片段作为上下文供 LLM 生成答案

## indexer.py
def build_knowledge_base():
    texts, metadatas = [], []
    for filename in os.listdir(DOCS_DIR):
        filepath = os.path.join(DOCS_DIR, filename)
        content = load_document(filepath)          #调用 document_loader 读取文档内容
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)  #切块实例对象
        chunks = splitter.split_text(content) #开始切，返回一个 文本块列表 chunks
        for i, chunk in enumerate(chunks): #列表中提取 块内容和块索引
            texts.append(chunk) #内容在一个列表
            metadatas.append({"source": filename, "chunk_id": i}) #元数据在一个列表：文件名、块在该文档中的序号
    collection.add(documents=texts, metadatas=metadatas, ids=ids) #内容列表和元数据列表拼在集合里，指定每个文档的唯一标识符列表

遍历 knowledge/ 下所有支持的文件
调用 document_loader.py 提取文本
切块、生成向量、存入 Chroma

## document_loader.py

扩展名	解析库	函数
.pdf	pypdf	PdfReader().extract_text()
.docx	python-docx	Document().paragraphs
.pptx	python-pptx	遍历 slides 和 shapes
.md	markdown + BeautifulSoup	转 HTML 后提取文本
.txt	内置 open	直接读取

支持格式：.pdf, .docx, .pptx, .md, .txt
每种格式有独立的解析函数

## app.py —— Streamlit Web 界面

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    answer = react_agent(prompt)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

提供用户友好的 Web 聊天界面，支持对话历史记录、清空历史、侧边栏信息。

## logger_config.py —— 日志配置

from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="{time} | {level} | {message}", level="INFO")
logger.add("agent.log", rotation="500 MB", level="DEBUG")

配置 Loguru 日志，同时输出到控制台（INFO 级别）和文件（DEBUG 级别，自动轮转）。

双输出：控制台只显示重要信息，文件记录详细 DEBUG 日志，便于排查问题。
自动轮转：agent.log 超过 500 MB 自动切分，避免磁盘占满。


### 整体数据流图

用户 → app.py (Streamlit) → react_agent.py → call_llm (azure_llm.py)
                                    ↓
                              extract_action
                                    ↓
                              tools 字典
                           ↙           ↘
                weather_tool.py    rag_tool.py
                     ↓                   ↓
                和风天气 API         Chroma 检索
                     ↓                   ↓
                 observation        observation
                                    ↓
                拼接回 prompt，循环，直至 Final Answer
                                    ↓
                返回答案 → app.py 显示
                
总结
react_agent.py 是核心调度器，依赖 azure_llm.py 和工具模块。

工具模块（weather_tool.py, rag_tool.py）各自独立，通过 tools 字典注册。

RAG 索引（indexer.py + document_loader.py）离线运行，将知识库向量化。

Web 界面（app.py）提供交互，通过 st.session_state 管理历史。

日志与配置（logger_config.py, .env）提供可观测性和安全性。


### 📋 环境变量说明
变量名	说明
AZURE_OPENAI_ENDPOINT	Azure OpenAI 资源终结点
AZURE_OPENAI_KEY	Azure OpenAI 密钥
AZURE_OPENAI_DEPLOYMENT	部署名称（例如 gpt-35-turbo）
HEFENG_KEY	和风天气 API Key

### 🧪 测试与调试
测试检索：python test_retrieve.py

查看数据库内容：python check_db.py

单独测试天气：python weather_tool.py

查看日志：实时输出在控制台，详细日志保存在 agent.log

### ⚠️ 注意事项
首次运行 indexer.py 会自动下载嵌入模型（约 130 MB），请保持网络通畅。

Chroma 数据库默认存储在项目根目录的 chroma_db/ 文件夹，请勿手动修改。

如果修改了嵌入模型或切块策略，需要删除 chroma_db/ 文件夹并重新索引。

天气 API 的免费版有调用次数限制，请合理使用。

## 📄 开源协议
MIT License

## 🤝 致谢
和风天气 API

Azure OpenAI

LangChain, Chroma, Streamlit, Loguru 等优秀开源项目

