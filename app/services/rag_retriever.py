import os
import json
from typing import Any, Dict, List

try:
    import chromadb
    from chromadb.utils import embedding_functions
    from chromadb.config import Settings
except Exception:
    chromadb = None
    embedding_functions = None
    Settings = None


CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", os.path.join("data", "chroma_db"))
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "my_knowledge")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", os.path.join("data", "processed_laborlaw"))
ENABLE_CHROMA_RETRIEVAL = os.getenv("ENABLE_CHROMA_RETRIEVAL", "false").lower() == "true"
CHONGQING_LOCAL_COLLECTION = os.getenv("CHONGQING_LOCAL_COLLECTION", "chongqing_labor_local_sources")
LABORLAW_NAVIGATOR_COLLECTION = os.getenv("LABORLAW_NAVIGATOR_COLLECTION", "laborlaw_navigator_curated")
EXTERNAL_DATA_DIR = os.getenv("EXTERNAL_DATA_DIR", os.path.join("data", "external_datasets"))
_fallback_docs: List[str] | None = None


def _get_collection():
    if not ENABLE_CHROMA_RETRIEVAL:
        raise RuntimeError("Chroma retrieval disabled")
    if chromadb is None or embedding_functions is None or Settings is None:
        raise RuntimeError("ChromaDB is not available")
    persist_dir_abs = os.path.abspath(CHROMA_PERSIST_DIR)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)

    # 兼容“目录不存在”的首次启动场景：Chroma 会创建目录与集合
    client = chromadb.PersistentClient(
        path=persist_dir_abs,
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=embedding_fn,
    )
    return collection


def retrieve_context(query: str, top_k: int = 3) -> List[str]:
    """
    使用 Chroma 向量库召回与 query 最相关的文档片段。
    返回 List[str]，由上层节点写入 state.context_data。
    """

    if not query.strip():
        return []

    local_docs = _retrieve_chongqing_local_sources(query, min(top_k, 3))
    if local_docs:
        navigator_docs = _retrieve_laborlaw_navigator_curated(query, max(0, top_k - len(local_docs)))
        return (local_docs + navigator_docs)[:top_k]

    try:
        collection = _get_collection()
        results = collection.query(query_texts=[query], n_results=top_k)
        docs = results.get("documents", [[]])[0] or []
    except Exception:
        docs = _retrieve_from_processed_files(query, top_k)

    # chromadb 返回可能包含非字符串时，做防御性转换
    out: List[str] = []
    for d in docs:
        if d is None:
            continue
        out.append(str(d))
    if len(out) < top_k:
        out.extend(_retrieve_laborlaw_navigator_curated(query, top_k - len(out)))
    return out


def _retrieve_laborlaw_navigator_curated(query: str, top_k: int) -> List[str]:
    if top_k <= 0:
        return []
    try:
        from app.services.local_embedding import embed_text

        if chromadb is None or Settings is None:
            return []
        client = chromadb.PersistentClient(
            path=os.path.abspath(CHROMA_PERSIST_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        collection = client.get_collection(name=LABORLAW_NAVIGATOR_COLLECTION)
        if collection.count() == 0:
            return []
        results = collection.query(
            query_embeddings=[embed_text(query)],
            n_results=top_k,
            include=["documents", "metadatas"],
        )
        documents = results.get("documents", [[]])[0] or []
        metadatas = results.get("metadatas", [[]])[0] or []
        out = []
        seen_sources = set()
        for idx, document in enumerate(documents):
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            source_file = metadata.get("source_file", "")
            if source_file and source_file in seen_sources:
                continue
            if source_file:
                seen_sources.add(source_file)
            out.append(_format_source_document(str(document), metadata))
        return out
    except Exception:
        return []


def _retrieve_chongqing_local_sources(query: str, top_k: int) -> List[str]:
    """Retrieve from the curated Chongqing local source collection first."""
    docs = _retrieve_chongqing_local_from_chroma(query, top_k)
    if docs:
        return docs
    return _retrieve_chongqing_local_from_json(query, top_k)


def _retrieve_chongqing_local_from_chroma(query: str, top_k: int) -> List[str]:
    try:
        from app.services.local_embedding import embed_text

        if chromadb is None or Settings is None:
            return []
        client = chromadb.PersistentClient(
            path=os.path.abspath(CHROMA_PERSIST_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        collection = client.get_collection(name=CHONGQING_LOCAL_COLLECTION)
        if collection.count() == 0:
            return []
        results = collection.query(
            query_embeddings=[embed_text(query)],
            n_results=top_k,
            include=["documents", "metadatas"],
        )
        documents = results.get("documents", [[]])[0] or []
        metadatas = results.get("metadatas", [[]])[0] or []
        out = []
        for idx, document in enumerate(documents):
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            out.append(_format_source_document(str(document), metadata))
        return out
    except Exception:
        return []


def _retrieve_chongqing_local_from_json(query: str, top_k: int) -> List[str]:
    path = os.path.join(EXTERNAL_DATA_DIR, "chongqing_labor_local_sources.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            records = json.load(f)
    except Exception:
        return []
    if not isinstance(records, list):
        return []

    tokens = _query_tokens(query)
    scored = []
    for record in records:
        if not isinstance(record, dict):
            continue
        searchable = json.dumps(record, ensure_ascii=False)
        token_score = sum(searchable.count(token) for token in tokens)
        score = token_score
        if token_score > 0 and "重庆" in searchable:
            score += 2
        if score > 0:
            scored.append((score, record))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [_format_local_record(record) for _, record in scored[:top_k]]


def _format_local_record(record: Dict[str, Any]) -> str:
    key_points = record.get("key_points") or []
    key_point_text = "；".join(str(item) for item in key_points[:4])
    return (
        f"重庆本地参考: {record.get('title', '')}\n"
        f"来源: {record.get('issuing_authority', '')} {record.get('date', '')}\n"
        f"链接: {record.get('url', '')}\n"
        f"类型: {record.get('case_type', '')}\n"
        f"适用场景: {record.get('scenario', '')}\n"
        f"摘要: {record.get('summary', '')}\n"
        f"要点: {key_point_text}"
    )


def _format_source_document(document: str, metadata: Dict[str, Any]) -> str:
    if not metadata:
        return document
    return (
        f"{document}\n"
        f"来源元数据: {metadata.get('issuing_authority', '')} "
        f"{metadata.get('date', '')} {metadata.get('url', '')}"
    )


def _query_tokens(query: str) -> List[str]:
    normalized = query.replace("，", " ").replace("。", " ").replace("、", " ")
    tokens = [token for token in normalized.split() if token]
    if len(tokens) <= 1:
        tokens.extend([query[i : i + 2] for i in range(max(0, len(query) - 1))])
    return tokens


def _retrieve_from_processed_files(query: str, top_k: int) -> List[str]:
    """
    Chroma 或本地 embedding 不可用时，从已处理 JSON 文档做轻量关键词召回。
    """
    global _fallback_docs
    if _fallback_docs is None:
        _fallback_docs = []
        for filename in [
            "regulation_documents.json",
            "guideline_documents.json",
            "case_documents.json",
            "other_documents.json",
        ]:
            path = os.path.join(PROCESSED_DATA_DIR, filename)
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    items = json.load(f)
            except Exception:
                continue
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                content = str(item.get("content") or item.get("text") or item.get("summary") or "")
                title = str(item.get("title") or item.get("source") or "")
                if content:
                    _fallback_docs.append(f"{title}\n{content[:800]}")

        external_path = os.path.join(EXTERNAL_DATA_DIR, "chongqing_labor_local_sources.json")
        if os.path.exists(external_path):
            try:
                with open(external_path, "r", encoding="utf-8") as f:
                    records = json.load(f)
                if isinstance(records, list):
                    for record in records:
                        if isinstance(record, dict):
                            _fallback_docs.append(_format_local_record(record))
            except Exception:
                pass

    if not _fallback_docs:
        return []

    tokens = _query_tokens(query)
    scored = []
    for doc in _fallback_docs:
        score = sum(doc.count(token) for token in tokens)
        if any(keyword in doc for keyword in ["重庆", "劳动", "仲裁", "工资", "解除", "工伤"]):
            score += 1
        scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for score, doc in scored[:top_k] if score > 0] or _fallback_docs[:top_k]

