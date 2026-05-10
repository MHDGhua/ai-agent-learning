#!/usr/bin/env python3
"""
Import public Chongqing labor-dispute local sources into Chroma.

The dataset stores summarized, source-attributed records rather than full pages.
This keeps the RAG store useful while avoiding bulk copying public articles.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chromadb
from chromadb.config import Settings

from app.services.local_embedding import embed_texts


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "external_datasets" / "chongqing_labor_local_sources.json"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "data" / "chroma_db"))
CHROMA_COLLECTION = os.getenv("CHONGQING_LOCAL_COLLECTION", "chongqing_labor_local_sources")


def main() -> None:
    records = _load_records(DATASET_PATH)
    documents = [_format_document(record) for record in records]
    metadatas = [_metadata(record) for record in records]
    ids = [record["id"] for record in records]
    embeddings = embed_texts(documents)

    client = chromadb.PersistentClient(
        path=os.path.abspath(CHROMA_PERSIST_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(name=CHROMA_COLLECTION)
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(json.dumps({
        "imported": len(records),
        "collection": CHROMA_COLLECTION,
        "persist_dir": os.path.abspath(CHROMA_PERSIST_DIR),
        "dataset": str(DATASET_PATH),
        "total_documents": collection.count(),
    }, ensure_ascii=False, indent=2))


def _load_records(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Dataset must be a list")
    return data


def _format_document(record: Dict[str, Any]) -> str:
    key_points = "\n".join(f"- {item}" for item in record.get("key_points", []))
    keywords = "、".join(record.get("rag_keywords", []))
    return (
        f"标题: {record.get('title', '')}\n"
        f"类型: {record.get('type', '')}\n"
        f"发布/来源机构: {record.get('issuing_authority', '')}\n"
        f"日期: {record.get('date', '')}\n"
        f"来源链接: {record.get('url', '')}\n"
        f"案件/事项类型: {record.get('case_type', '')}\n"
        f"适用场景: {record.get('scenario', '')}\n"
        f"摘要: {record.get('summary', '')}\n"
        f"要点:\n{key_points}\n"
        f"检索关键词: {keywords}"
    )


def _metadata(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": record.get("id", ""),
        "type": record.get("type", ""),
        "title": record.get("title", ""),
        "case_type": record.get("case_type", ""),
        "issuing_authority": record.get("issuing_authority", ""),
        "date": record.get("date", ""),
        "url": record.get("url", ""),
        "jurisdiction": "重庆",
        "source_kind": "public_summary",
    }


if __name__ == "__main__":
    main()
