import os
import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi
import jieba

# ------------------ 初始化向量库 ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(
    name="my_knowledge",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name='BAAI/bge-small-zh-v1.5'
    )
)

# ------------------ 获取所有文档片段（用于 BM25）------------------
# 注意：如果文档很多，可以提前保存 BM25 索引，这里简化，每次查询时动态构建
def get_all_documents():
    """从 Chroma 中取出所有文档片段（仅文本）"""
    # 注意：如果 collection 很大，可以考虑分批取，这里假设小于 1000 条
    results = collection.get(include=["documents"])
    return results['documents']  # 返回列表

# 全局变量，只加载一次（在模块首次导入时）
_ALL_DOCS = None
_BM25_INDEX = None

def get_bm25_index():
    global _ALL_DOCS, _BM25_INDEX
    if _BM25_INDEX is None:
        _ALL_DOCS = get_all_documents()
        # 对每个文档进行中文分词
        tokenized_docs = [list(jieba.cut(doc)) for doc in _ALL_DOCS]
        _BM25_INDEX = BM25Okapi(tokenized_docs)
    return _BM25_INDEX, _ALL_DOCS

# ------------------ 混合检索函数 ------------------
def hybrid_search(query: str, top_k: int = 2, weight_vector: float = 0.5, weight_bm25: float = 0.5):
    """
    混合检索：同时使用向量检索和 BM25 检索，加权合并结果。
    """
    # 1. 向量检索
    vector_results = collection.query(query_texts=[query], n_results=top_k * 2)  # 多召回一些，供融合
    vector_docs = vector_results['documents'][0] if vector_results['documents'] else []
    # 向量检索本身已经按相似度排序，我们可以保留顺序分数（距离转分数）
    # 为了融合，我们给向量结果中每个文档一个分数（逆序排名）
    vector_scores = {doc: (len(vector_docs) - i) for i, doc in enumerate(vector_docs)} if vector_docs else {}

    # 2. BM25 检索
    bm25_index, all_docs = get_bm25_index()
    tokenized_query = list(jieba.cut(query))
    bm25_scores = bm25_index.get_scores(tokenized_query)  # 返回每个文档的 BM25 分数
    # 将分数映射到文档
    bm25_score_map = {all_docs[i]: bm25_scores[i] for i in range(len(all_docs))}

    # 3. 合并文档集（向量检索结果 + BM25 结果中分数 >0 的文档）
    candidate_docs = set(vector_docs) | {doc for doc, score in bm25_score_map.items() if score > 0}

    # 4. 计算每个文档的综合得分
    final_scores = {}
    for doc in candidate_docs:
        # 向量分数（如果没有，给 0）
        v_score = vector_scores.get(doc, 0)
        # 归一化 BM25 分数（原始分数范围不定，这里简单除以最大分数）
        b_score = bm25_score_map.get(doc, 0)
        # 避免除零
        max_bm25 = max(bm25_score_map.values()) if bm25_score_map else 1
        norm_b_score = b_score / max_bm25 if max_bm25 > 0 else 0
        # 综合得分
        final_scores[doc] = weight_vector * v_score + weight_bm25 * norm_b_score

    # 5. 排序取 top_k
    sorted_docs = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    best_docs = [doc for doc, score in sorted_docs]
    return "\n\n".join(best_docs) if best_docs else "未找到相关信息"

# 为了兼容原来的 retrieve_documents 接口，可以替换或新增函数
def retrieve_documents(query: str, top_k: int = 2) -> str:
    return hybrid_search(query, top_k=top_k, weight_vector=0.6, weight_bm25=0.4)